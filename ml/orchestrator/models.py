from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ml.features.models import LinguisticFeaturesResponse
from ml.ai_detection.models import AISignalsResponse
from ml.fingerprint.models import FingerprintComparisonResult
from ml.source_analysis.models import SourceSimilarityResult
from ml.paraphrase.models import ParaphraseResult
from ml.evidence_engine.models import EvidenceItem
from ml.explanation.models import ExplanationReport

class OrchestratorRequest(BaseModel):
    student_id: str
    assignment_name: str
    reference_sources: Optional[List[Dict[str, str]]] = None # list of {"id": "ref1", "text": "..."}

class OrchestratorResult(BaseModel):
    submission_id: str
    student_id: str
    assignment_name: str
    
    document_statistics: Dict[str, Any]
    linguistic_features: Optional[LinguisticFeaturesResponse]
    ai_linguistic_signals: Optional[AISignalsResponse]
    writing_fingerprint_comparison: Optional[FingerprintComparisonResult]
    source_similarity: Optional[SourceSimilarityResult]
    paraphrase_analysis: Optional[ParaphraseResult]
    
    evidence_list: List[EvidenceItem]
    risk_score: float
    risk_level: str
    confidence: str
    safeguard_warnings: List[str]
    
    gemini_explanation: Optional[ExplanationReport]
    
    analysis_timestamp: str
    errors: List[str]
