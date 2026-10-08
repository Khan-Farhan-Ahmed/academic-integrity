from pydantic import BaseModel
from typing import List, Optional

class ParaphraseRequest(BaseModel):
    source_text: str
    submitted_text: str

class ParaphraseResult(BaseModel):
    semantic_similarity: float
    lexical_similarity: float
    paraphrase_signal: float
    transformation_indicators: List[str]
    evidence_explanation: str
    error: Optional[str] = None
