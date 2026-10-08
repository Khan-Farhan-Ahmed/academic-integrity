from fastapi import APIRouter, HTTPException
from ml.explanation.models import ExplanationRequest, ExplanationResponse
from ml.explanation.service import generate_explanation

router = APIRouter()

@router.post("/explanation", response_model=ExplanationResponse)
async def get_explanation(request: ExplanationRequest):
    try:
        result = generate_explanation(request.evidence_result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")
