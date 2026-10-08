from pydantic import BaseModel
from typing import List, Optional

class WritingFingerprint(BaseModel):
    avg_sentence_length: float
    sentence_length_std: float
    vocabulary_diversity: float
    avg_word_length: float
    comma_ratio: float
    period_ratio: float
    paragraph_length_mean: float
    stopword_ratio: float
    long_word_ratio: float
    repeated_word_ratio: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    document_count: int = 1

class FeatureDeviation(BaseModel):
    feature_name: str
    baseline_value: float
    new_value: float
    deviation_percent: float
    impact_score: float

class FingerprintComparisonResult(BaseModel):
    style_similarity: float
    deviation_score: float
    per_feature_deviations: List[FeatureDeviation]
    top_style_changes: List[str]
    error: Optional[str] = None

class FingerprintCreateRequest(BaseModel):
    texts: List[str]

class FingerprintCompareRequest(BaseModel):
    baseline: WritingFingerprint
    new_text: str
