from fastapi import APIRouter, HTTPException
from ml.paraphrase.models import ParaphraseRequest, ParaphraseResult
from ml.paraphrase.service import calculate_paraphrase

router = APIRouter()

@router.post("/paraphrase", response_model=ParaphraseResult)
async def analyze_paraphrase(request: ParaphraseRequest):
    try:
        result = calculate_paraphrase(request.source_text, request.submitted_text)
        if result.error:
            raise HTTPException(status_code=400, detail=result.error)
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Paraphrasing analysis failed: {str(e)}")
