from typing import List
from ml.features.extractor import extract_features
from ml.fingerprint.models import WritingFingerprint, FeatureDeviation, FingerprintComparisonResult

def create_fingerprint_from_text(text: str) -> WritingFingerprint:
    features = extract_features(text)
    
    chars = max(features.basic.character_count, 1)
    
    return WritingFingerprint(
        avg_sentence_length=features.basic.average_sentence_length,
        sentence_length_std=features.sentence.sentence_length_std,
        vocabulary_diversity=features.vocabulary.vocabulary_diversity,
        avg_word_length=features.basic.average_word_length,
        comma_ratio=features.punctuation.comma_count / chars,
        period_ratio=features.punctuation.period_count / chars,
        paragraph_length_mean=features.patterns.paragraph_length_mean,
        stopword_ratio=features.patterns.stopword_ratio,
        long_word_ratio=features.patterns.long_word_ratio,
        repeated_word_ratio=features.patterns.repeated_word_ratio,
        flesch_reading_ease=features.readability.flesch_reading_ease,
        flesch_kincaid_grade=features.readability.flesch_kincaid_grade,
        document_count=1
    )

def aggregate_fingerprints(fingerprints: List[WritingFingerprint]) -> WritingFingerprint:
    if not fingerprints:
        return None
    if len(fingerprints) == 1:
        return fingerprints[0]
        
    total_docs = sum(f.document_count for f in fingerprints)
    
    def weighted_avg(field: str) -> float:
        total_weight = sum(getattr(f, field) * f.document_count for f in fingerprints)
        return total_weight / total_docs

    return WritingFingerprint(
        avg_sentence_length=weighted_avg("avg_sentence_length"),
        sentence_length_std=weighted_avg("sentence_length_std"),
        vocabulary_diversity=weighted_avg("vocabulary_diversity"),
        avg_word_length=weighted_avg("avg_word_length"),
        comma_ratio=weighted_avg("comma_ratio"),
        period_ratio=weighted_avg("period_ratio"),
        paragraph_length_mean=weighted_avg("paragraph_length_mean"),
        stopword_ratio=weighted_avg("stopword_ratio"),
        long_word_ratio=weighted_avg("long_word_ratio"),
        repeated_word_ratio=weighted_avg("repeated_word_ratio"),
        flesch_reading_ease=weighted_avg("flesch_reading_ease"),
        flesch_kincaid_grade=weighted_avg("flesch_kincaid_grade"),
        document_count=total_docs
    )

def create_baseline(texts: List[str]) -> WritingFingerprint:
    fps = [create_fingerprint_from_text(t) for t in texts if t.strip()]
    if not fps:
        # Return an empty baseline if texts are invalid
        return create_fingerprint_from_text("")
    return aggregate_fingerprints(fps)

def compare_fingerprints(baseline: WritingFingerprint, new_text: str) -> FingerprintComparisonResult:
    if not baseline:
        return FingerprintComparisonResult(
            style_similarity=0.0, deviation_score=0.0,
            per_feature_deviations=[], top_style_changes=[],
            error="No baseline provided"
        )
        
    if not new_text or not new_text.strip():
        return FingerprintComparisonResult(
            style_similarity=0.0, deviation_score=0.0,
            per_feature_deviations=[], top_style_changes=[],
            error="New text is empty or too short"
        )
        
    new_fp = create_fingerprint_from_text(new_text)
    
    features_to_compare = [
        "avg_sentence_length", "sentence_length_std", "vocabulary_diversity",
        "avg_word_length", "comma_ratio", "period_ratio", "paragraph_length_mean",
        "stopword_ratio", "long_word_ratio", "repeated_word_ratio",
        "flesch_reading_ease", "flesch_kincaid_grade"
    ]
    
    deviations = []
    total_impact = 0.0
    
    for feature in features_to_compare:
        b_val = getattr(baseline, feature)
        n_val = getattr(new_fp, feature)
        
        diff = abs(b_val - n_val)
        # Avoid division by zero
        denom = max(abs(b_val), 0.0001)
        
        dev_percent = (diff / denom) * 100.0
        # Cap deviation percent to avoid extreme outliers exploding the score
        dev_percent = min(dev_percent, 200.0)
        
        # Map 0-100% diff to 0-10 impact score
        impact = min(dev_percent / 10.0, 10.0) 
        
        deviations.append(FeatureDeviation(
            feature_name=feature,
            baseline_value=b_val,
            new_value=n_val,
            deviation_percent=dev_percent,
            impact_score=impact
        ))
        
        total_impact += impact

    max_impact = len(features_to_compare) * 10.0
    deviation_score = (total_impact / max_impact) * 100.0
    style_similarity = max(0.0, 100.0 - deviation_score)
    
    deviations.sort(key=lambda x: x.impact_score, reverse=True)
    top_changes = []
    for d in deviations[:3]:
        if d.impact_score > 3.0:
            direction = "increased" if d.new_value > d.baseline_value else "decreased"
            top_changes.append(f"{d.feature_name} significantly {direction} (change: {d.deviation_percent:.1f}%)")
            
    return FingerprintComparisonResult(
        style_similarity=style_similarity,
        deviation_score=deviation_score,
        per_feature_deviations=deviations,
        top_style_changes=top_changes
    )
