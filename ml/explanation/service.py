import os
import json
from google import genai
from pydantic import BaseModel
from ml.evidence_engine.models import EvidenceEngineResult
from ml.explanation.models import ExplanationReport, ExplanationResponse

def generate_explanation(evidence: EvidenceEngineResult) -> ExplanationResponse:
    # Always provide a fallback explanation
    fallback_report = ExplanationReport(
        executive_summary="An automated analysis was performed on the submission.",
        main_evidence_findings=["Evidence Engine risk score calculated."],
        why_each_finding_matters=["The calculated risk score indicates the presence of unexpected patterns."],
        conflicting_weak_evidence=["Automated analysis is inherently limited and statistical."],
        limitations=["This system provides heuristic flags, not definitive proof of AI generation."],
        recommended_instructor_action="Instructor review is recommended to verify the evidence."
    )
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ExplanationResponse(
            report=fallback_report,
            success=False,
            error="GEMINI_API_KEY is not set."
        )
        
    client = genai.Client(api_key=api_key)
    
    system_instruction = (
        "You are a neutral, objective academic integrity assistant. "
        "Your job is to translate statistical and heuristic evidence into a clear, "
        "non-accusatory report for an instructor. "
        "NEVER say 'The student cheated', 'This is 100% AI generated', or make absolute claims. "
        "Always use language like 'The submission shows signals associated with...', "
        "'The evidence suggests...', or 'Instructor review is recommended.' "
        "The Evidence Engine is the source of truth. Do not make up evidence or independent conclusions."
    )
    
    prompt = f"""
    Analyze the following output from the Academic Integrity Evidence Engine:
    
    Overall Risk Score: {evidence.overall_risk_score}
    Risk Level: {evidence.risk_level}
    Evidence Strength: {evidence.evidence_strength}
    Confidence: {evidence.confidence}
    Conclusion: {evidence.conclusion}
    
    Safeguards/Warnings: {evidence.safeguard_warnings}
    
    Detailed Evidence Items:
    {json.dumps([item.model_dump() for item in evidence.evidence_items], indent=2)}
    
    Based on this data, provide a structured explanation report.
    """
    
    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
            system_instruction=system_instruction,
            response_format=[
                {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ExplanationReport.model_json_schema(),
                }
            ],
            # Do not use store=False unless required, but tests might mock this
        )
        
        if not interaction.output_text:
            raise ValueError("Empty response from Gemini")
            
        # Parse JSON output
        parsed_report_dict = json.loads(interaction.output_text)
        report = ExplanationReport(**parsed_report_dict)
        
        return ExplanationResponse(
            report=report,
            success=True
        )
    except Exception as e:
        return ExplanationResponse(
            report=fallback_report,
            success=False,
            error=str(e)
        )
