from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.models.documents import DocumentExtractionResponse
from backend.services.extraction import extract_text
from backend.api.auth import get_current_user, User

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

@router.post("/upload", response_model=DocumentExtractionResponse)
async def api_upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Extract text
    extracted_text = extract_text(content, file.filename, file.content_type)
    
    if not extracted_text:
        raise HTTPException(status_code=400, detail="No readable text found in document.")
        
    return DocumentExtractionResponse(
        filename=file.filename,
        file_type=file.content_type,
        character_count=len(extracted_text),
        word_count=len(extracted_text.split()),
        extracted_text=extracted_text
    )
