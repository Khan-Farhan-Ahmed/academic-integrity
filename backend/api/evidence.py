from fastapi import APIRouter, HTTPException
from ml.evidence_engine.models import EvidenceEngineRequest, EvidenceEngineResult
from ml.evidence_engine.service import calculate_evidence

router = APIRouter()

@router.post("/evidence", response_model=EvidenceEngineResult)
async def analyze_evidence(request: EvidenceEngineRequest):
    try:
        return calculate_evidence(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence generation failed: {str(e)}")
