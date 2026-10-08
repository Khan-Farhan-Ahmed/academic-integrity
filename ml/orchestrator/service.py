import datetime
import traceback
from typing import List, Dict, Any, Optional
from ml.orchestrator.models import OrchestratorResult

# Import all core services
from backend.services.extraction import extract_text
from ml.features.extractor import extract_features
from ml.ai_detection.engine import analyze_signals
from ml.fingerprint.service import compare_fingerprints
from ml.source_analysis.service import calculate_similarity
from ml.source_analysis.models import ReferenceDocument
from ml.paraphrase.service import calculate_paraphrase
from ml.evidence_engine.service import calculate_evidence
from ml.evidence_engine.models import EvidenceEngineRequest
from ml.explanation.service import generate_explanation

# Database Repository
from backend.db.repository import DatabaseRepository

def run_orchestrator(
    student_id: str,
    assignment_name: str,
    filename: str,
    file_type: str,
    file_bytes: bytes,
    reference_sources: Optional[List[Dict[str, str]]] = None
) -> OrchestratorResult:
    
    errors: List[str] = []
    repo = DatabaseRepository()
    
    # 1. Start submission tracking
    submission_id = "temp_" + str(datetime.datetime.now().timestamp())
    try:
        db_sub = repo.save_submission(student_id, assignment_name)
        if db_sub and "id" in db_sub:
            submission_id = db_sub["id"]
    except Exception as e:
        errors.append(f"DB submission failed: {str(e)}")

    # 2. Text Extraction
    try:
        extracted_text = extract_text(file_bytes, filename, file_type)
        if not extracted_text:
            return _bail_out(submission_id, student_id, assignment_name, "No readable text found in document.")
            
        char_count = len(extracted_text)
        word_count = len(extracted_text.split())
        
        try:
            repo.save_document(submission_id, filename, file_type, char_count, word_count, extracted_text)
        except Exception as e:
            errors.append(f"DB document failed: {str(e)}")
            
    except Exception as e:
        return _bail_out(submission_id, student_id, assignment_name, f"Text extraction failed: {str(e)}")

    if word_count < 10:
        return _bail_out(submission_id, student_id, assignment_name, "Document is too short for any meaningful analysis.")

    # Prevent massive files from exhausting API limits
    if word_count > 25000:
        # Truncate text to approx 25k words (taking the first 25k)
        extracted_text = " ".join(extracted_text.split()[:25000])
        errors.append("Document exceeded 25,000 words. Analysis was truncated to the first 25,000 words.")

    # 3. Feature Extraction
    features = None
    try:
        features = extract_features(extracted_text)
    except Exception as e:
        errors.append(f"Feature extraction failed: {str(e)}")

    # 4. AI Writing Signals
    ai_signals = None
    try:
        ai_signals = analyze_signals(extracted_text)
    except Exception as e:
        errors.append(f"AI signals failed: {str(e)}")

    # 5. Writing Fingerprint Comparison
    fingerprint = None
    try:
        # Since baseline retrieval isn't fully implemented in the db layer yet, pass None
        fingerprint = compare_fingerprints(None, extracted_text)
        if fingerprint.error:
            errors.append(f"Fingerprint info: {fingerprint.error}")
    except Exception as e:
        errors.append(f"Fingerprint comparison failed: {str(e)}")

    # 6. Source Similarity
    source_similarity = None
    paraphrase = None
    if reference_sources:
        try:
            refs = [ReferenceDocument(id=r["id"], text=r["text"]) for r in reference_sources]
            source_similarity = calculate_similarity(extracted_text, refs)
            
            # 7. Paraphrase Analysis
            # If there's a strong match, we might analyze paraphrasing against the top matched source
            if source_similarity and source_similarity.top_matches:
                top_match_id = source_similarity.top_matches[0].reference_id
                matched_ref_text = next((r.text for r in refs if r.id == top_match_id), None)
                if matched_ref_text:
                    paraphrase = calculate_paraphrase(matched_ref_text, extracted_text)
                    if paraphrase.error:
                         errors.append(f"Paraphrase info: {paraphrase.error}")
        except Exception as e:
            errors.append(f"Source similarity/paraphrase failed: {str(e)}")

    # 8. Save Analysis Results to DB
    try:
        repo.save_analysis_results(
            submission_id,
            linguistic=features.model_dump() if features else None,
            ai_signals=ai_signals.model_dump() if ai_signals else None,
            source_similarity=source_similarity.model_dump() if source_similarity else None,
            paraphrase=paraphrase.model_dump() if paraphrase else None,
            fingerprint=fingerprint.model_dump() if fingerprint else None
        )
    except Exception as e:
         errors.append(f"DB analysis results failed: {str(e)}")

    # 9. Evidence Engine
    evidence_engine_result = None
    try:
        req = EvidenceEngineRequest(
            word_count=word_count,
            ai_signals=ai_signals,
            fingerprint_comparison=fingerprint,
            source_similarity=source_similarity,
            paraphrase_analysis=paraphrase
        )
        evidence_engine_result = calculate_evidence(req)
        
        try:
            repo.save_evidence(submission_id, [item.model_dump() for item in evidence_engine_result.evidence_items])
        except Exception as e:
            errors.append(f"DB evidence failed: {str(e)}")
            
    except Exception as e:
        errors.append(f"Evidence engine failed: {str(e)}")
        # We need a fallback evidence result if it completely crashed
        from ml.evidence_engine.models import EvidenceEngineResult
        evidence_engine_result = EvidenceEngineResult(
            overall_risk_score=0.0,
            risk_level="LOW",
            evidence_strength="LOW",
            confidence="LOW",
            evidence_items=[],
            safeguard_warnings=["Evidence engine completely failed."],
            conclusion="Analysis failed."
        )

    # 10. Gemini Explanation
    explanation = None
    try:
        explanation_res = generate_explanation(evidence_engine_result)
        explanation = explanation_res.report
        if not explanation_res.success:
            errors.append(f"Explanation info: {explanation_res.error}")
    except Exception as e:
        errors.append(f"Explanation failed: {str(e)}")

    # 11. Persist Report
    try:
        repo.save_report(
            submission_id,
            evidence_engine_result.overall_risk_score,
            evidence_engine_result.risk_level,
            evidence_engine_result.evidence_strength,
            evidence_engine_result.confidence,
            evidence_engine_result.safeguard_warnings,
            evidence_engine_result.conclusion,
            explanation.model_dump() if explanation else None
        )
    except Exception as e:
         errors.append(f"DB report failed: {str(e)}")

    return OrchestratorResult(
        submission_id=submission_id,
        student_id=student_id,
        assignment_name=assignment_name,
        document_statistics={"character_count": char_count, "word_count": word_count},
        linguistic_features=features,
        ai_linguistic_signals=ai_signals,
        writing_fingerprint_comparison=fingerprint,
        source_similarity=source_similarity,
        paraphrase_analysis=paraphrase,
        evidence_list=evidence_engine_result.evidence_items,
        risk_score=evidence_engine_result.overall_risk_score,
        risk_level=evidence_engine_result.risk_level,
        confidence=evidence_engine_result.confidence,
        safeguard_warnings=evidence_engine_result.safeguard_warnings,
        gemini_explanation=explanation,
        analysis_timestamp=datetime.datetime.now().isoformat(),
        errors=errors
    )

def _bail_out(submission_id: str, student_id: str, assignment_name: str, error_msg: str) -> OrchestratorResult:
    # Partial failure where we can't even extract text
    return OrchestratorResult(
        submission_id=submission_id,
        student_id=student_id,
        assignment_name=assignment_name,
        document_statistics={},
        linguistic_features=None,
        ai_linguistic_signals=None,
        writing_fingerprint_comparison=None,
        source_similarity=None,
        paraphrase_analysis=None,
        evidence_list=[],
        risk_score=0.0,
        risk_level="LOW",
        confidence="LOW",
        safeguard_warnings=[error_msg],
        gemini_explanation=None,
        analysis_timestamp=datetime.datetime.now().isoformat(),
        errors=[error_msg]
    )
