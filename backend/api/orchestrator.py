from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
import json
import logging
from ml.orchestrator.models import OrchestratorResult
from ml.orchestrator.service import run_orchestrator
from backend.api.auth import get_instructor_user, User
from backend.db.repository import DatabaseRepository

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIMES = [
    "text/plain", 
    "application/pdf", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

@router.post("/run", response_model=OrchestratorResult)
async def api_run_analysis_pipeline(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    assignment_name: str = Form(...),
    reference_sources_json: Optional[str] = Form(None),
    current_user: User = Depends(get_instructor_user)
):
    # 1. File Validation
    if file.content_type not in ALLOWED_MIMES:
        logger.warning(f"Rejected file upload due to MIME type: {file.content_type}")
        raise HTTPException(status_code=415, detail="Unsupported file type. Only TXT, PDF, and DOCX are allowed.")
        
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        logger.warning(f"Rejected file upload due to size: {len(file_bytes)} bytes")
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 2. Authorization (Verify instructor owns student)
    repo = DatabaseRepository()
    try:
        # Check if student exists and belongs to current_user
        sb_client = repo.client
        if sb_client:
            stu_res = sb_client.table("students").select("user_id").eq("id", student_id).execute()
            if not stu_res.data or stu_res.data[0].get("user_id") != current_user.id:
                logger.warning(f"Unauthorized access attempt to student {student_id} by user {current_user.id}")
                raise HTTPException(status_code=403, detail="Not authorized to access this student.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DB verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal database error during authorization.")

    # 3. Parse references
    reference_sources = None
    if reference_sources_json:
        try:
            reference_sources = json.loads(reference_sources_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for reference_sources")
            
    # 4. Execute Pipeline
    try:
        logger.info(f"Starting pipeline for student_id={student_id}, filename={file.filename}")
        result = run_orchestrator(
            student_id=student_id,
            assignment_name=assignment_name,
            filename=file.filename,
            file_type=file.content_type,
            file_bytes=file_bytes,
            reference_sources=reference_sources
        )
        return result
    except Exception as e:
        logger.error(f"Pipeline execution failed critically: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal pipeline execution error.")
