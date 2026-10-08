from pydantic import BaseModel
from typing import List

class SignalResult(BaseModel):
    name: str
    score: float
    explanation: str

class AISignalsResponse(BaseModel):
    signals: List[SignalResult]
    ai_linguistic_signal: float
