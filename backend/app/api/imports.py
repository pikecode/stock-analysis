"""Import API."""
import os
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.models.stock import ImportBatch, MetricType
from app.services.import_service import ImportService
from app.services.optimized_csv_import import OptimizedCSVImportService
from app.services.optimized_txt_import import OptimizedTXTImportService
from app.services.compute_service import ComputeService
from app.schemas.stock import ImportBatchResponse, ImportUploadResponse

router = APIRouter(prefix="/admin/import", tags=["Import"])


@router.post("/upload", response_model=ImportUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(..., description="CSV or TXT"),
    metric_code: Optional[str] = Form(None, description="Metric code for TXT files"),
    data_date: Optional[str] = Form(None, description="Data date for TXT files (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Upload file for import - Admin only."""
    # Validate file type
    file_type = file_type.upper()
    if file_type not in ("CSV", "TXT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file_type must be CSV or TXT",
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes",
        )

    import_service = ImportService(db)

    # For TXT files, validate metric type
    metric_type_id = None
    parsed_date = None

    if file_type == "TXT":
        # Try to parse date from parameter or filename
        if data_date:
            try:
                parsed_date = date.fromisoformat(data_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid data_date format. Use YYYY-MM-DD",
                )
        else:
            # Try to extract date from filename
            parsed_date = import_service.extract_date_from_filename(file.filename)
            if not parsed_date:
                # Try to extract date from file content
                parsed_date = import_service.extract_date_from_content(file_content)
            if not parsed_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot extract date from filename or file content. Please provide data_date parameter",
                )

        # Auto-detect or use provided metric code
        if metric_code:
            metric_type = import_service.get_metric_type(metric_code.upper())
        else:
            metric_type = import_service.detect_metric_type(file.filename)

        if not metric_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot determine metric type. Please provide metric_code",
            )

        metric_type_id = metric_type.id

    # Create batch record
    try:
        batch = import_service.create_batch(
            file_name=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_content=file_content,
            metric_type_id=metric_type_id,
            data_date=parsed_date,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Save file temporarily
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{batch.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Process synchronously for small files, async for large files
    if file_size < 1024 * 1024:  # 1MB
        # Process synchronously
        try:
            if file_type == "CSV":
                import_service.update_batch_status(batch.id, "processing")
                csv_service = OptimizedCSVImportService(db)
                success, errors = csv_service.parse_and_import_optimized(batch.id, file_content)
                import_service.update_batch_status(
                    batch.id, "completed",
                    total_rows=success + errors,
                    success_rows=success,
                    error_rows=errors,
                )
            else:
                import_service.update_batch_status(batch.id, "processing")
                metric_type = import_service.get_metric_type_by_id(metric_type_id)

                # Delete old data for the same metric type and date
                import_service.delete_old_metric_data(metric_type_id, parsed_date, batch.id)

                # Use optimized TXT import service (includes computation)
                txt_service = OptimizedTXTImportService(db)
                success, errors = txt_service.parse_and_import_with_compute(
                    batch.id, file_content, metric_type_id, metric_type.code, parsed_date
                )
                import_service.update_batch_status(
                    batch.id, "completed",
                    total_rows=success + errors,
                    success_rows=success,
                    error_rows=errors,
                )

            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)

            db.refresh(batch)
            return ImportUploadResponse(
                batch_id=batch.id,
                file_name=file.filename,
                status=batch.status,
                message="Import completed successfully",
            )

        except Exception as e:
            import_service.update_batch_status(batch.id, "failed", error_message=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import failed: {str(e)}",
            )
    else:
        # Queue for async processing
        from tasks.import_tasks import process_csv_import, process_txt_import

        if file_type == "CSV":
            process_csv_import.delay(batch.id, file_path)
        else:
            process_txt_import.delay(
                batch.id, file_path, metric_type_id, data_date
            )

        return ImportUploadResponse(
            batch_id=batch.id,
            file_name=file.filename,
            status="pending",
            message="File uploaded. Processing in background",
        )


@router.get("/batches", response_model=list[ImportBatchResponse])
async def list_batches(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Get import batch list - Admin only."""
    query = db.query(ImportBatch).order_by(ImportBatch.created_at.desc())

    if status:
        query = query.filter(ImportBatch.status == status)

    offset = (page - 1) * page_size
    batches = query.offset(offset).limit(page_size).all()

    result = []
    for b in batches:
        metric_code = None
        if b.metric_type:
            metric_code = b.metric_type.code

        result.append(
            ImportBatchResponse(
                id=b.id,
                file_name=b.file_name,
                file_type=b.file_type,
                metric_code=metric_code,
                data_date=b.data_date,
                status=b.status,
                compute_status=b.compute_status,
                total_rows=b.total_rows,
                success_rows=b.success_rows,
                error_rows=b.error_rows,
                started_at=b.started_at,
                completed_at=b.completed_at,
                created_at=b.created_at,
            )
        )

    return result


@router.get("/batches/{batch_id}", response_model=ImportBatchResponse)
async def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Get import batch detail - Admin only."""
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found",
        )

    metric_code = None
    if batch.metric_type:
        metric_code = batch.metric_type.code

    return ImportBatchResponse(
        id=batch.id,
        file_name=batch.file_name,
        file_type=batch.file_type,
        metric_code=metric_code,
        data_date=batch.data_date,
        status=batch.status,
        compute_status=batch.compute_status,
        total_rows=batch.total_rows,
        success_rows=batch.success_rows,
        error_rows=batch.error_rows,
        started_at=batch.started_at,
        completed_at=batch.completed_at,
        created_at=batch.created_at,
    )


@router.post("/batches/{batch_id}/recompute")
async def recompute_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Recompute rankings and summaries for a batch - Admin only."""
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found",
        )

    if batch.file_type != "TXT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recompute is only available for TXT imports",
        )

    # Recompute synchronously for now
    compute_service = ComputeService(db)
    compute_service.compute_all_for_batch(batch_id)

    return {
        "batch_id": batch_id,
        "compute_status": "completed",
        "message": "Recompute completed successfully",
    }


@router.get("/metrics", response_model=list)
async def list_metrics(db: Session = Depends(get_db)):
    """Get available metric types."""
    metrics = db.query(MetricType).filter(MetricType.is_active == True).all()
    return [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "file_pattern": m.file_pattern,
        }
        for m in metrics
    ]
