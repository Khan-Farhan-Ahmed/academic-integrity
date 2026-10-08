from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ml.features.extractor import extract_features
from ml.features.models import LinguisticFeaturesResponse

router = APIRouter()

class FeatureAnalysisRequest(BaseModel):
    text: str

@router.post("/features", response_model=LinguisticFeaturesResponse)
async def analyze_features(request: FeatureAnalysisRequest):
    try:
        features = extract_features(request.text)
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")
