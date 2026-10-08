from pydantic import BaseModel
from typing import List, Optional
from ml.evidence_engine.models import EvidenceEngineResult

class ExplanationReport(BaseModel):
    executive_summary: str
    main_evidence_findings: List[str]
    why_each_finding_matters: List[str]
    conflicting_weak_evidence: List[str]
    limitations: List[str]
    recommended_instructor_action: str

class ExplanationRequest(BaseModel):
    evidence_result: EvidenceEngineResult

class ExplanationResponse(BaseModel):
    report: ExplanationReport
    success: bool
    error: Optional[str] = None
