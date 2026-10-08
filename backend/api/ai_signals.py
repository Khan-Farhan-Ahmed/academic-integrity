from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ml.ai_detection.engine import analyze_signals
from ml.ai_detection.models import AISignalsResponse

router = APIRouter()

class AISignalsRequest(BaseModel):
    text: str

@router.post("/ai-signals", response_model=AISignalsResponse)
async def get_ai_signals(request: AISignalsRequest):
    try:
        response = analyze_signals(request.text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal analysis failed: {str(e)}")
