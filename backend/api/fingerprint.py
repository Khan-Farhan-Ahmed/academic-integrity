from fastapi import APIRouter, HTTPException
from ml.fingerprint.models import FingerprintCreateRequest, FingerprintCompareRequest, WritingFingerprint, FingerprintComparisonResult
from ml.fingerprint.service import create_baseline, compare_fingerprints

router = APIRouter()

@router.post("/create", response_model=WritingFingerprint)
async def create_fingerprint(request: FingerprintCreateRequest):
    try:
        baseline = create_baseline(request.texts)
        if not baseline:
            raise HTTPException(status_code=400, detail="Failed to create baseline from provided texts.")
        return baseline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fingerprint creation failed: {str(e)}")

@router.post("/compare", response_model=FingerprintComparisonResult)
async def compare_fingerprint(request: FingerprintCompareRequest):
    try:
        result = compare_fingerprints(request.baseline, request.new_text)
        if result.error:
            raise HTTPException(status_code=400, detail=result.error)
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Fingerprint comparison failed: {str(e)}")
