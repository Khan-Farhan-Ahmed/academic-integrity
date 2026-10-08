import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ml.embeddings.service import get_raw_embeddings
from ml.paraphrase.models import ParaphraseResult
from ml.features.extractor import extract_features

def get_ngrams(words: list[str], n: int) -> set:
    if len(words) < n:
        return set()
    return set(tuple(words[i:i+n]) for i in range(len(words)-n+1))

def calculate_paraphrase(source_text: str, submitted_text: str) -> ParaphraseResult:
    if not source_text or not source_text.strip():
        return ParaphraseResult(
            semantic_similarity=0.0,
            lexical_similarity=0.0,
            paraphrase_signal=0.0,
            transformation_indicators=[],
            evidence_explanation="Insufficient evidence: No source text supplied for comparison.",
            error="Missing source text"
        )
        
    if not submitted_text or not submitted_text.strip():
        return ParaphraseResult(
            semantic_similarity=0.0,
            lexical_similarity=0.0,
            paraphrase_signal=0.0,
            transformation_indicators=[],
            evidence_explanation="Insufficient evidence: Submitted text is empty.",
            error="Missing submitted text"
        )
        
    # Get word arrays
    source_words = [w.lower() for w in re.findall(r'\w+', source_text)]
    sub_words = [w.lower() for w in re.findall(r'\w+', submitted_text)]
    
    if len(source_words) < 5 or len(sub_words) < 5:
        return ParaphraseResult(
            semantic_similarity=0.0,
            lexical_similarity=0.0,
            paraphrase_signal=0.0,
            transformation_indicators=[],
            evidence_explanation="Insufficient evidence: Texts are too short to reliably detect paraphrasing.",
            error="Texts too short"
        )
        
    # Semantic similarity
    try:
        embeds = get_raw_embeddings([source_text, submitted_text])
        if len(embeds) == 2:
            sem_sim = float(cosine_similarity([embeds[0]], [embeds[1]])[0][0]) * 100.0
        else:
            sem_sim = 0.0
    except Exception:
        sem_sim = 0.0
        
    sem_sim = max(0.0, min(sem_sim, 100.0))
    
    # Lexical overlap
    source_set = set(source_words)
    sub_set = set(sub_words)
    
    word_overlap = len(source_set.intersection(sub_set)) / max(len(source_set.union(sub_set)), 1)
    
    source_3grams = get_ngrams(source_words, 3)
    sub_3grams = get_ngrams(sub_words, 3)
    ngram_overlap = len(source_3grams.intersection(sub_3grams)) / max(len(source_3grams.union(sub_3grams)), 1)
    
    # Combine lexical metrics
    lexical_similarity = ((word_overlap * 0.4) + (ngram_overlap * 0.6)) * 100.0
    
    indicators = []
    
    # Feature extraction for structural changes
    source_feat = extract_features(source_text)
    sub_feat = extract_features(submitted_text)
    
    # Transformation Logic
    paraphrase_signal = 0.0
    
    if sem_sim > 75.0 and lexical_similarity < 40.0:
        indicators.append("High semantic similarity combined with low lexical overlap indicates heavy synonym replacement.")
        paraphrase_signal += 50.0
        
    if sem_sim > 85.0 and lexical_similarity < 60.0:
        paraphrase_signal += 30.0
        
    if abs(source_feat.basic.sentence_count - sub_feat.basic.sentence_count) > 2 and sem_sim > 70.0:
        indicators.append("Sentence restructuring detected: Number of sentences changed while preserving semantic meaning.")
        paraphrase_signal += 15.0
        
    if abs(source_feat.basic.average_sentence_length - sub_feat.basic.average_sentence_length) > 5 and sem_sim > 70.0:
        indicators.append("Changed sentence lengths detected, suggesting structural transformation.")
        paraphrase_signal += 10.0
        
    # Cap signal
    paraphrase_signal = min(paraphrase_signal, 100.0)
    
    explanation = "No significant paraphrasing detected."
    if paraphrase_signal > 75.0:
        explanation = "Strong paraphrasing-like transformation detected. Semantic meaning is highly preserved while structure and vocabulary are heavily altered."
    elif paraphrase_signal > 40.0:
        explanation = "Moderate paraphrasing-like transformation detected. Some evidence of lexical rewriting."
        
    return ParaphraseResult(
        semantic_similarity=sem_sim,
        lexical_similarity=lexical_similarity,
        paraphrase_signal=paraphrase_signal,
        transformation_indicators=indicators,
        evidence_explanation=explanation
    )
