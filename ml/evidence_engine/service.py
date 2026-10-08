import uuid
from typing import List, Dict, Any
from ml.evidence_engine.models import EvidenceEngineRequest, EvidenceEngineResult, EvidenceItem

# Configurable Base Weights
WEIGHTS = {
    "AI_LINGUISTIC": 25.0,
    "STYLE_DEVIATION": 30.0,
    "SOURCE_SIMILARITY": 45.0,
    "PARAPHRASE": 35.0
}

def determine_severity(score: float) -> str:
    if score > 75: return "HIGH"
    if score > 40: return "MEDIUM"
    return "LOW"

def calculate_evidence(request: EvidenceEngineRequest) -> EvidenceEngineResult:
    evidence_items: List[EvidenceItem] = []
    safeguards: List[str] = []
    
    if request.word_count < 50:
        safeguards.append("Submission is very short. Analysis reliability is severely degraded.")
        
    active_weights_sum = 0.0
    weighted_risk_sum = 0.0
    
    # 1. AI Linguistic Signals
    if request.ai_signals:
        if request.ai_signals.ai_linguistic_signal > 0 or len(request.ai_signals.signals) > 1:
            score = request.ai_signals.ai_linguistic_signal
            weight = WEIGHTS["AI_LINGUISTIC"]
            active_weights_sum += weight
            risk_contrib = score * (weight / 100.0)
            weighted_risk_sum += risk_contrib
            
            reliability = "HIGH" if request.word_count > 200 else ("MEDIUM" if request.word_count > 50 else "LOW")
            
            evidence_items.append(EvidenceItem(
                evidence_id=str(uuid.uuid4()),
                category="AI linguistic patterns",
                signal_name="AI Linguistic Signal",
                score=score,
                severity=determine_severity(score),
                description="Analysis of sentence uniformity, repetition, and stylistic mechanics.",
                supporting_metrics={"top_signals": [s.name for s in request.ai_signals.signals if s.score > 50]},
                reliability=reliability,
                contribution_to_risk=risk_contrib
            ))
            
    # 2. Writing Style Deviation
    if request.fingerprint_comparison:
        if request.fingerprint_comparison.error:
            safeguards.append(f"Style baseline issue: {request.fingerprint_comparison.error}")
        else:
            score = request.fingerprint_comparison.deviation_score
            weight = WEIGHTS["STYLE_DEVIATION"]
            active_weights_sum += weight
            risk_contrib = score * (weight / 100.0)
            weighted_risk_sum += risk_contrib
            
            evidence_items.append(EvidenceItem(
                evidence_id=str(uuid.uuid4()),
                category="Writing style deviation",
                signal_name="Fingerprint Deviation",
                score=score,
                severity=determine_severity(score),
                description="Comparison against the student's known historical writing style.",
                supporting_metrics={"top_changes": request.fingerprint_comparison.top_style_changes},
                reliability="MEDIUM", # Style can change naturally
                contribution_to_risk=risk_contrib
            ))
            
    # 3. Source Similarity
    if request.source_similarity:
        score = request.source_similarity.strong_match_percentage
        if request.source_similarity.overall_similarity_score > 0:
            # Boost score based on average similarity of strong matches
            score = min(100.0, score + (request.source_similarity.overall_similarity_score * 0.2))
            
        weight = WEIGHTS["SOURCE_SIMILARITY"]
        active_weights_sum += weight
        risk_contrib = score * (weight / 100.0)
        weighted_risk_sum += risk_contrib
        
        evidence_items.append(EvidenceItem(
            evidence_id=str(uuid.uuid4()),
            category="Source similarity",
            signal_name="Direct Semantic Match",
            score=score,
            severity=determine_severity(score),
            description="Identification of chunks directly overlapping semantically with provided sources.",
            supporting_metrics={"top_source_matched": request.source_similarity.top_matches[0].reference_id if request.source_similarity.top_matches else None},
            reliability="HIGH",
            contribution_to_risk=risk_contrib
        ))

    # 4. Paraphrase Transformation
    if request.paraphrase_analysis:
        if request.paraphrase_analysis.error:
            if "Missing source text" not in request.paraphrase_analysis.error:
                safeguards.append(f"Paraphrase issue: {request.paraphrase_analysis.error}")
        else:
            score = request.paraphrase_analysis.paraphrase_signal
            weight = WEIGHTS["PARAPHRASE"]
            active_weights_sum += weight
            risk_contrib = score * (weight / 100.0)
            weighted_risk_sum += risk_contrib
            
            evidence_items.append(EvidenceItem(
                evidence_id=str(uuid.uuid4()),
                category="Paraphrase-like transformation",
                signal_name="Structural Rewriting",
                score=score,
                severity=determine_severity(score),
                description="Detection of high semantic similarity combined with severe lexical alteration.",
                supporting_metrics={"indicators": request.paraphrase_analysis.transformation_indicators},
                reliability="MEDIUM",
                contribution_to_risk=risk_contrib
            ))

    if active_weights_sum == 0:
        safeguards.append("Insufficient evidence to run the risk engine.")
        return EvidenceEngineResult(
            overall_risk_score=0.0,
            risk_level="LOW",
            evidence_strength="LOW",
            confidence="LOW",
            evidence_items=[],
            safeguard_warnings=safeguards,
            conclusion="Not enough data to calculate risk."
        )

    # Normalize risk score out of 100
    overall_risk_score = (weighted_risk_sum / active_weights_sum) * 100.0
    overall_risk_score = min(overall_risk_score, 100.0)
    
    # Check for conflicting signals (e.g. style deviation very high but source similarity is 0, or vice versa)
    # We define a conflict if the standard deviation of valid component scores is extremely high.
    scores = [item.score for item in evidence_items]
    import numpy as np
    std_dev = np.std(scores) if len(scores) > 1 else 0
    if std_dev > 40:
        safeguards.append("Conflicting signals detected. Some analysis modules strongly indicate risk while others indicate none.")

    # Risk level mapping
    if overall_risk_score > 65:
        risk_level = "HIGH"
    elif overall_risk_score > 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    # Evidence strength depends on how many categories fired highly
    high_items = len([i for i in evidence_items if i.severity == "HIGH"])
    if high_items >= 2:
        evidence_strength = "HIGH"
    elif high_items == 1 or len([i for i in evidence_items if i.severity == "MEDIUM"]) >= 2:
        evidence_strength = "MEDIUM"
    else:
        evidence_strength = "LOW"
        
    # Confidence depends on active inputs and length
    if len(evidence_items) >= 3 and request.word_count >= 150:
        confidence = "HIGH"
    elif len(evidence_items) >= 2 and request.word_count >= 50:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"
        
    # Conclusion generation (Must not claim definite AI or cheating)
    if risk_level == "HIGH":
        conclusion = "High investigation risk. Strong evidence requires instructor review."
    elif risk_level == "MEDIUM":
        conclusion = "Moderate investigation risk. Review recommended based on mixed evidence."
    else:
        conclusion = "Low investigation risk. No significant structural or semantic anomalies found."

    return EvidenceEngineResult(
        overall_risk_score=overall_risk_score,
        risk_level=risk_level,
        evidence_strength=evidence_strength,
        confidence=confidence,
        evidence_items=evidence_items,
        safeguard_warnings=safeguards,
        conclusion=conclusion
    )
