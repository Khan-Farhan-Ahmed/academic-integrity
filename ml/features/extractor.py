import spacy
import textstat
import numpy as np
from collections import Counter
from ml.features.models import (
    BasicStatistics, VocabularyFeatures, SentenceVariation,
    PunctuationFeatures, ReadabilityFeatures, LinguisticPatterns,
    LinguisticFeaturesResponse
)

# Load spacy model globally to avoid loading overhead per request
try:
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm", disable=["ner"])

def get_empty_features() -> LinguisticFeaturesResponse:
    return LinguisticFeaturesResponse(
        basic=BasicStatistics(character_count=0, word_count=0, sentence_count=0, paragraph_count=0, average_word_length=0.0, average_sentence_length=0.0),
        vocabulary=VocabularyFeatures(unique_word_count=0, vocabulary_diversity=0.0, hapax_ratio=0.0),
        sentence=SentenceVariation(sentence_length_mean=0.0, sentence_length_std=0.0, sentence_length_min=0, sentence_length_max=0),
        punctuation=PunctuationFeatures(comma_count=0, period_count=0, semicolon_count=0, colon_count=0, question_mark_count=0, exclamation_mark_count=0),
        readability=ReadabilityFeatures(flesch_reading_ease=0.0, flesch_kincaid_grade=0.0),
        patterns=LinguisticPatterns(stopword_ratio=0.0, long_word_ratio=0.0, repeated_word_ratio=0.0, paragraph_length_mean=0.0, paragraph_length_std=0.0)
    )

def extract_features(text: str) -> LinguisticFeaturesResponse:
    if not text or not text.strip():
        return get_empty_features()

    # Preprocessing
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    paragraph_lengths = [len(p.split()) for p in paragraphs]

    doc = nlp(text)
    
    words = [token.text.lower() for token in doc if token.is_alpha]
    word_count = len(words)
    character_count = len(text)
    
    sentences = list(doc.sents)
    sentence_count = len(sentences)
    
    if word_count == 0:
        return get_empty_features()

    # Basic Statistics
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    basic = BasicStatistics(
        character_count=character_count,
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        average_word_length=avg_word_length,
        average_sentence_length=avg_sentence_length
    )

    # Vocabulary
    word_freq = Counter(words)
    unique_words = len(word_freq)
    vocab_diversity = unique_words / word_count if word_count > 0 else 0
    hapax_legomena = sum(1 for count in word_freq.values() if count == 1)
    hapax_ratio = hapax_legomena / word_count if word_count > 0 else 0
    
    vocabulary = VocabularyFeatures(
        unique_word_count=unique_words,
        vocabulary_diversity=vocab_diversity,
        hapax_ratio=hapax_ratio
    )

    # Sentence Variation
    sent_lengths = [len([t for t in s if t.is_alpha]) for s in sentences]
    if sent_lengths:
        sent_len_mean = float(np.mean(sent_lengths))
        sent_len_std = float(np.std(sent_lengths))
        sent_len_min = int(np.min(sent_lengths))
        sent_len_max = int(np.max(sent_lengths))
    else:
        sent_len_mean, sent_len_std, sent_len_min, sent_len_max = 0.0, 0.0, 0, 0

    sentence_variation = SentenceVariation(
        sentence_length_mean=sent_len_mean,
        sentence_length_std=sent_len_std,
        sentence_length_min=sent_len_min,
        sentence_length_max=sent_len_max
    )

    # Punctuation
    punctuation = PunctuationFeatures(
        comma_count=text.count(','),
        period_count=text.count('.'),
        semicolon_count=text.count(';'),
        colon_count=text.count(':'),
        question_mark_count=text.count('?'),
        exclamation_mark_count=text.count('!')
    )

    # Readability
    try:
        fre = textstat.flesch_reading_ease(text)
        fkg = textstat.flesch_kincaid_grade(text)
    except Exception:
        fre, fkg = 0.0, 0.0

    readability = ReadabilityFeatures(
        flesch_reading_ease=fre,
        flesch_kincaid_grade=fkg
    )

    # Linguistic Patterns
    stopwords = [t for t in doc if t.is_stop and t.is_alpha]
    stopword_ratio = len(stopwords) / word_count if word_count > 0 else 0
    long_words = [w for w in words if len(w) > 6]
    long_word_ratio = len(long_words) / word_count if word_count > 0 else 0
    
    # Simple repeated word heuristic (adjacent duplicates)
    repeated_words = 0
    for i in range(1, len(words)):
        if words[i] == words[i-1]:
            repeated_words += 1
    repeated_word_ratio = repeated_words / word_count if word_count > 0 else 0

    if paragraph_lengths:
        para_len_mean = float(np.mean(paragraph_lengths))
        para_len_std = float(np.std(paragraph_lengths))
    else:
        para_len_mean, para_len_std = 0.0, 0.0

    patterns = LinguisticPatterns(
        stopword_ratio=stopword_ratio,
        long_word_ratio=long_word_ratio,
        repeated_word_ratio=repeated_word_ratio,
        paragraph_length_mean=para_len_mean,
        paragraph_length_std=para_len_std
    )

    return LinguisticFeaturesResponse(
        basic=basic,
        vocabulary=vocabulary,
        sentence=sentence_variation,
        punctuation=punctuation,
        readability=readability,
        patterns=patterns
    )
