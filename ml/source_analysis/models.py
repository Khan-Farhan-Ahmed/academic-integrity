from pydantic import BaseModel
from typing import List, Optional

class ReferenceDocument(BaseModel):
    id: str
    text: str

class MatchDetail(BaseModel):
    submission_chunk: str
    reference_id: str
    reference_chunk: str
    similarity_score: float

class SourceSimilarityResult(BaseModel):
    overall_similarity_score: float  # Weighted or max overall representation
    strong_match_percentage: float   # % of submission with strong matches
    top_matches: List[MatchDetail]

class SourceSimilarityRequest(BaseModel):
    submission_text: str
    reference_documents: List[ReferenceDocument]
    threshold: float = 0.85
