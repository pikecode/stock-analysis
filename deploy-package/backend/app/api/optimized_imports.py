"""优化后的导入API"""
import os
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks, Query
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.stock import ImportBatch, MetricType
from app.services.import_service import ImportService
from app.services.optimized_csv_import import OptimizedCSVImportService
from app.services.optimized_txt_import import OptimizedTXTImportService
from app.services.parallel_import_service import ParallelTXTImportService, AsyncImportQueue
from app.services.cache_service import CacheService, ImportStatusCache
from app.schemas.stock import ImportBatchResponse, ImportUploadResponse

router = APIRouter(prefix="/import/v2", tags=["Optimized Import"])

# 初始化服务
cache_service = CacheService(settings.REDIS_URL)
import_status_cache = ImportStatusCache(cache_service)

# 异步导入队列（全局单例）
async_queue = AsyncImportQueue(max_concurrent_imports=3)


@router.post("/upload/optimized", response_model=ImportUploadResponse)
async def upload_file_optimized(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = Form(..., description="CSV or TXT"),
    metric_code: Optional[str] = Form(None, description="Metric code for TXT files"),
    data_date: Optional[str] = Form(None, description="Data date (YYYY-MM-DD)"),
    use_parallel: bool = Form(False, description="Use parallel processing for large files"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    优化版文件上传接口

    特性：
    - CSV文件：优化的批量导入，预加载缓存
    - TXT文件：内存计算排名，COPY命令批量插入
    - 大文件：支持并行处理（use_parallel=true）
    - 进度追踪：通过Redis缓存实时更新进度
    """

    # 验证文件类型
    file_type = file_type.upper()
    if file_type not in ("CSV", "TXT"):
        raise HTTPException(status_code=400, detail="file_type must be CSV or TXT")

    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)

    # 验证文件大小
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
        )

    import_service = ImportService(db)

    # 处理TXT文件的指标类型和日期
    metric_type_id = None
    parsed_date = None

    if file_type == "TXT":
        # 解析日期
        if data_date:
            try:
                parsed_date = date.fromisoformat(data_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        else:
            parsed_date = import_service.extract_date_from_filename(file.filename)
            if not parsed_date:
                parsed_date = import_service.extract_date_from_content(file_content)
            if not parsed_date:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot determine date. Please provide data_date parameter"
                )

        # 获取指标类型
        if metric_code:
            metric_type = import_service.get_metric_type(metric_code.upper())
        else:
            metric_type = import_service.detect_metric_type(file.filename)

        if not metric_type:
            raise HTTPException(
                status_code=400,
                detail="Cannot determine metric type. Please provide metric_code"
            )

        metric_type_id = metric_type.id

    # 创建批次记录
    batch = import_service.create_batch(
        file_name=file.filename,
        file_type=file_type,
        file_size=file_size,
        file_content=file_content,
        metric_type_id=metric_type_id,
        data_date=parsed_date,
        user_id=current_user.id,
    )

    # 初始化进度
    import_status_cache.update_import_progress(
        batch.id, current=0, total=100, status="pending"
    )

    # 判断处理方式
    if file_size > 10 * 1024 * 1024 and use_parallel:  # 10MB以上且启用并行
        # 使用并行处理
        background_tasks.add_task(
            process_large_file_parallel,
            batch.id,
            file_content,
            file_type,
            metric_type_id,
            parsed_date,
            db
        )
        return ImportUploadResponse(
            batch_id=batch.id,
            file_name=file.filename,
            status="processing",
            message="Large file processing in parallel mode"
        )

    elif file_size > 1024 * 1024:  # 1MB以上异步处理
        # 添加到异步队列
        task_info = {
            'batch_id': batch.id,
            'file_content': file_content,
            'file_type': file_type,
            'metric_type_id': metric_type_id,
            'metric_code': metric_type.code if metric_type else None,
            'data_date': parsed_date
        }
        async_queue.add_import_task(task_info)

        return ImportUploadResponse(
            batch_id=batch.id,
            file_name=file.filename,
            status="queued",
            message="File queued for processing"
        )

    else:
        # 小文件同步处理
        try:
            success, errors = process_file_sync(
                batch.id,
                file_content,
                file_type,
                metric_type_id,
                parsed_date,
                db
            )

            import_service.update_batch_status(
                batch.id, "completed",
                total_rows=success + errors,
                success_rows=success,
                error_rows=errors
            )

            return ImportUploadResponse(
                batch_id=batch.id,
                file_name=file.filename,
                status="completed",
                message=f"Import completed: {success} success, {errors} errors"
            )

        except Exception as e:
            import_service.update_batch_status(batch.id, "failed", error_message=str(e))
            raise HTTPException(status_code=500, detail=str(e))


def process_file_sync(
    batch_id: int,
    file_content: bytes,
    file_type: str,
    metric_type_id: Optional[int],
    data_date: Optional[date],
    db: Session
) -> tuple:
    """同步处理文件"""

    if file_type == "CSV":
        service = OptimizedCSVImportService(db)
        return service.parse_and_import_optimized(batch_id, file_content)
    else:
        # TXT文件
        import_service = ImportService(db)
        metric_type = import_service.get_metric_type_by_id(metric_type_id)

        # 删除旧数据
        import_service.delete_old_metric_data(metric_type_id, data_date, batch_id)

        # 使用优化的导入服务
        service = OptimizedTXTImportService(db)
        return service.parse_and_import_with_compute(
            batch_id,
            file_content,
            metric_type_id,
            metric_type.code,
            data_date
        )


async def process_large_file_parallel(
    batch_id: int,
    file_content: bytes,
    file_type: str,
    metric_type_id: Optional[int],
    data_date: Optional[date],
    db: Session
):
    """并行处理大文件"""

    try:
        # 更新进度
        import_status_cache.update_import_progress(
            batch_id, current=10, total=100, status="processing"
        )

        # 创建session factory用于多线程
        engine = create_engine(settings.DATABASE_URL)
        SessionFactory = sessionmaker(bind=engine)

        if file_type == "TXT":
            # 获取metric信息
            import_service = ImportService(db)
            metric_type = import_service.get_metric_type_by_id(metric_type_id)

            # 删除旧数据
            import_service.delete_old_metric_data(metric_type_id, data_date, batch_id)

            # 使用并行导入服务
            service = ParallelTXTImportService(SessionFactory)
            success, errors = service.process_large_file(
                file_content,
                batch_id,
                metric_type_id,
                metric_type.code,
                data_date,
                num_workers=4
            )

            # 更新批次状态
            import_service.update_batch_status(
                batch_id, "completed",
                total_rows=success + errors,
                success_rows=success,
                error_rows=errors
            )

        # 更新完成进度
        import_status_cache.update_import_progress(
            batch_id, current=100, total=100, status="completed"
        )

    except Exception as e:
        import_status_cache.update_import_progress(
            batch_id, current=0, total=100, status="failed"
        )
        # 更新批次状态
        import_service = ImportService(db)
        import_service.update_batch_status(batch_id, "failed", error_message=str(e))


@router.get("/progress/{batch_id}")
async def get_import_progress(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取导入进度"""

    # 从缓存获取进度
    progress = import_status_cache.get_import_progress(batch_id)

    if not progress:
        # 从数据库获取批次信息
        batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        progress = {
            "batch_id": batch_id,
            "status": batch.status,
            "total_rows": batch.total_rows or 0,
            "success_rows": batch.success_rows or 0,
            "error_rows": batch.error_rows or 0
        }

    return progress


@router.get("/queue/status")
async def get_queue_status(current_user: User = Depends(get_current_user)):
    """获取导入队列状态"""
    return async_queue.get_status()


@router.post("/cache/clear")
async def clear_cache(
    cache_type: str = Query(..., description="Cache type: rankings, summaries, or all"),
    current_user: User = Depends(get_current_user)
):
    """清除缓存"""

    if cache_type == "rankings":
        cache_service.delete_pattern("ranking:*")
        message = "Rankings cache cleared"
    elif cache_type == "summaries":
        cache_service.delete_pattern("summary:*")
        message = "Summaries cache cleared"
    elif cache_type == "all":
        cache_service.delete_pattern("*")
        message = "All cache cleared"
    else:
        raise HTTPException(status_code=400, detail="Invalid cache type")

    return {"message": message}


@router.post("/optimize/database")
async def optimize_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行数据库优化"""

    try:
        # 更新统计信息
        db.execute("ANALYZE stocks")
        db.execute("ANALYZE concepts")
        db.execute("ANALYZE stock_concepts")
        db.execute("ANALYZE stock_metric_data_raw")
        db.execute("ANALYZE concept_stock_daily_rank")
        db.execute("ANALYZE concept_daily_summary")

        # 清理过期数据
        db.execute("SELECT cleanup_old_imports(30)")

        # 刷新物化视图（如果存在）
        try:
            db.execute("SELECT refresh_materialized_views()")
        except:
            pass

        db.commit()

        return {"message": "Database optimization completed"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))