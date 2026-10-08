from fastapi import APIRouter, HTTPException
from ml.source_analysis.models import SourceSimilarityRequest, SourceSimilarityResult
from ml.source_analysis.service import calculate_similarity

router = APIRouter()

@router.post("/source-similarity", response_model=SourceSimilarityResult)
async def analyze_source_similarity(request: SourceSimilarityRequest):
    try:
        result = calculate_similarity(
            request.submission_text, 
            request.reference_documents, 
            request.threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source similarity analysis failed: {str(e)}")
