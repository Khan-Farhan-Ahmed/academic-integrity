from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# These models represent the inputs the engine can take.
from ml.ai_detection.models import AISignalsResponse
from ml.fingerprint.models import FingerprintComparisonResult
from ml.source_analysis.models import SourceSimilarityResult
from ml.paraphrase.models import ParaphraseResult

class EvidenceItem(BaseModel):
    evidence_id: str
    category: str
    signal_name: str
    score: float
    severity: str
    description: str
    supporting_metrics: Dict[str, Any]
    reliability: str
    contribution_to_risk: float

class EvidenceEngineRequest(BaseModel):
    # Optional inputs from previous stages
    ai_signals: Optional[AISignalsResponse] = None
    fingerprint_comparison: Optional[FingerprintComparisonResult] = None
    source_similarity: Optional[SourceSimilarityResult] = None
    paraphrase_analysis: Optional[ParaphraseResult] = None
    
    # Simple word count directly to check bounds if feature extractor is missing
    word_count: int

class EvidenceEngineResult(BaseModel):
    overall_risk_score: float
    risk_level: str
    evidence_strength: str
    confidence: str
    evidence_items: List[EvidenceItem]
    safeguard_warnings: List[str]
    conclusion: str
