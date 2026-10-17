from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import os
from ..database import get_db
from ..models.user import User
from ..models.account import Account
from ..models.workspace import Workspace
from ..schemas.import_job import (
    ImportJobCreate, ImportPreviewRequest, ImportPreviewResponse,
    ImportConfirmRequest, ImportConfirmResponse
)
from ..services.import_service import (
    create_import_job, process_csv_preview, confirm_import
)
from ..dependencies import get_current_user

router = APIRouter(prefix="/imports", tags=["imports"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=201)
async def upload_csv(
    account_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify account ownership
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE/1024/1024}MB)")
    
    job_id = uuid4()
    filepath = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    job = create_import_job(
        db=db,
        job_id=job_id,
        workspace_id=workspace.id,
        account_id=account_id,
        filename=file.filename,
        filepath=filepath,
    )
    
    return {
        "job_id": str(job.id),
        "filename": job.filename,
        "status": job.status,
    }

@router.post("/preview/{job_id}", response_model=ImportPreviewResponse)
def preview_import(
    job_id: UUID,
    request: ImportPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ..models.import_job import ImportJob
    
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == job.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = process_csv_preview(
        db=db,
        job_id=job_id,
        workspace_id=workspace.id,
        column_mapping=request.column_mapping,
        date_format=request.date_format,
        decimal_separator=request.decimal_separator,
    )
    
    return result

@router.post("/confirm/{job_id}", response_model=ImportConfirmResponse)
def confirm_csv_import(
    job_id: UUID,
    request: ImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ..models.import_job import ImportJob
    
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == job.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = confirm_import(
        db=db,
        job_id=job_id,
        workspace_id=workspace.id,
        row_numbers=request.row_numbers,
    )
    
    return result

@router.get("/jobs")
def list_import_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ..models.import_job import ImportJob
    
    workspace_ids = [w.id for w in db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()]
    
    jobs = db.query(ImportJob).filter(
        ImportJob.workspace_id.in_(workspace_ids)
    ).order_by(ImportJob.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": str(job.id),
            "filename": job.filename,
            "status": job.status,
            "total_rows": job.total_rows,
            "imported_rows": job.imported_rows,
            "created_at": job.created_at.isoformat(),
        }
        for job in jobs
    ]
