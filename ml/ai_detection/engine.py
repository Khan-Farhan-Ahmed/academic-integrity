from ml.features.extractor import extract_features
from ml.ai_detection.models import SignalResult, AISignalsResponse

def analyze_signals(text: str) -> AISignalsResponse:
    features = extract_features(text)
    
    signals = []
    
    if features.basic.word_count < 10:
        return AISignalsResponse(
            signals=[SignalResult(
                name="Insufficient Data", 
                score=0.0, 
                explanation="Text is too short to generate meaningful linguistic signals."
            )],
            ai_linguistic_signal=0.0
        )
        
    # Signal 1: Sentence Length Consistency
    mean_sl = features.sentence.sentence_length_mean
    std_sl = features.sentence.sentence_length_std
    
    cv = std_sl / mean_sl if mean_sl > 0 else 0
    if cv == 0:
        sl_score = 100.0
        sl_exp = "Sentences are identically long, showing unnatural uniformity."
    elif cv < 0.25:
        sl_score = 85.0
        sl_exp = "Sentence lengths are highly consistent, common in generated text."
    elif cv < 0.4:
        sl_score = 50.0
        sl_exp = "Sentence length variation is moderately consistent."
    else:
        sl_score = 15.0
        sl_exp = "Natural variation in sentence lengths."
        
    signals.append(SignalResult(name="Sentence Uniformity", score=sl_score, explanation=sl_exp))
    
    # Signal 2: Vocabulary Diversity
    div = features.vocabulary.vocabulary_diversity
    if div < 0.3:
        div_score = 90.0
        div_exp = "Vocabulary diversity is unusually low."
    elif div < 0.5:
        div_score = 50.0
        div_exp = "Vocabulary diversity is typical."
    else:
        div_score = 10.0
        div_exp = "Rich vocabulary diversity."
        
    signals.append(SignalResult(name="Vocabulary Stylistic Signal", score=div_score, explanation=div_exp))
    
    # Signal 3: Repetition Patterns
    rep = features.patterns.repeated_word_ratio
    if rep > 0.05:
        rep_score = 90.0
        rep_exp = "Excessive adjacent word repetition detected."
    elif rep > 0.02:
        rep_score = 60.0
        rep_exp = "Moderate word repetition patterns."
    else:
        rep_score = 10.0
        rep_exp = "Few repeated adjacent words."
        
    signals.append(SignalResult(name="Repetition Indicators", score=rep_score, explanation=rep_exp))
    
    # Signal 4: Paragraph Length Consistency
    mean_pl = features.patterns.paragraph_length_mean
    std_pl = features.patterns.paragraph_length_std
    if features.basic.paragraph_count > 1 and mean_pl > 0:
        cv_pl = std_pl / mean_pl
        if cv_pl < 0.15:
            pl_score = 90.0
            pl_exp = "Paragraph lengths are highly uniform, indicating potential mechanical generation."
        elif cv_pl < 0.35:
            pl_score = 50.0
            pl_exp = "Moderate variation in paragraph lengths."
        else:
            pl_score = 15.0
            pl_exp = "Natural variation in paragraph lengths."
    else:
        pl_score = 0.0
        pl_exp = "Not enough paragraphs to evaluate consistency."
        
    signals.append(SignalResult(name="Paragraph Uniformity", score=pl_score, explanation=pl_exp))

    # Signal 5: Long Word Distribution
    lw_ratio = features.patterns.long_word_ratio
    if lw_ratio > 0.35:
        lw_score = 80.0
        lw_exp = "Unusually high density of long words, sometimes seen in overly formal generated text."
    elif lw_ratio > 0.2:
        lw_score = 40.0
        lw_exp = "Normal distribution of complex words."
    else:
        lw_score = 10.0
        lw_exp = "Simple vocabulary distribution."
        
    signals.append(SignalResult(name="Complexity Patterns", score=lw_score, explanation=lw_exp))

    # Calculate overall ai_linguistic_signal
    # Average of active scores (ignore paragraph uniformity if only 1 paragraph)
    active_scores = [s.score for s in signals if s.name != "Paragraph Uniformity" or features.basic.paragraph_count > 1]
    overall = sum(active_scores) / len(active_scores) if active_scores else 0.0
    
    return AISignalsResponse(signals=signals, ai_linguistic_signal=overall)
