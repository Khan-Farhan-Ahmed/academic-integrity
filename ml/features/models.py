from pydantic import BaseModel

class BasicStatistics(BaseModel):
    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    average_word_length: float
    average_sentence_length: float

class VocabularyFeatures(BaseModel):
    unique_word_count: int
    vocabulary_diversity: float
    hapax_ratio: float

class SentenceVariation(BaseModel):
    sentence_length_mean: float
    sentence_length_std: float
    sentence_length_min: int
    sentence_length_max: int

class PunctuationFeatures(BaseModel):
    comma_count: int
    period_count: int
    semicolon_count: int
    colon_count: int
    question_mark_count: int
    exclamation_mark_count: int

class ReadabilityFeatures(BaseModel):
    flesch_reading_ease: float
    flesch_kincaid_grade: float

class LinguisticPatterns(BaseModel):
    stopword_ratio: float
    long_word_ratio: float
    repeated_word_ratio: float
    paragraph_length_mean: float
    paragraph_length_std: float

class LinguisticFeaturesResponse(BaseModel):
    basic: BasicStatistics
    vocabulary: VocabularyFeatures
    sentence: SentenceVariation
    punctuation: PunctuationFeatures
    readability: ReadabilityFeatures
    patterns: LinguisticPatterns
