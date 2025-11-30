"""Import tasks for Celery."""
import os
from datetime import date

from tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.import_service import ImportService
from app.services.optimized_csv_import import OptimizedCSVImportService
from app.services.optimized_txt_import import OptimizedTXTImportService


@celery_app.task(bind=True, name="tasks.process_csv_import")
def process_csv_import(self, batch_id: int, file_path: str):
    """Process CSV file import (async)."""
    db = SessionLocal()
    try:
        import_service = ImportService(db)

        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # 调用统一导入方法
        success_count, error_count = import_service.import_csv_file(batch_id, file_content)

        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "batch_id": batch_id,
            "status": "completed",
            "success_rows": success_count,
            "error_rows": error_count,
        }

    except Exception as e:
        import_service.update_batch_status(batch_id, "failed", error_message=str(e))
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.process_txt_import")
def process_txt_import(
    self,
    batch_id: int,
    file_path: str,
    metric_type_id: int,
    data_date_str: str,
):
    """Process TXT file import (async) - includes computation."""
    db = SessionLocal()
    try:
        import_service = ImportService(db)

        # Parse data date
        data_date = date.fromisoformat(data_date_str)

        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # 调用统一导入方法
        success_count, error_count = import_service.import_txt_file(
            batch_id, file_content, metric_type_id, data_date
        )

        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "batch_id": batch_id,
            "status": "completed",
            "success_rows": success_count,
            "error_rows": error_count,
            "compute_status": "completed",
        }

    except Exception as e:
        import_service.update_batch_status(batch_id, "failed", error_message=str(e))
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.recompute_batch")
def recompute_batch(self, batch_id: int):
    """Recompute rankings and summaries for a batch."""
    db = SessionLocal()
    try:
        import_service = ImportService(db)
        compute_service = ComputeService(db)

        import_service.update_compute_status(batch_id, "computing")
        compute_service.compute_all_for_batch(batch_id)

        return {
            "batch_id": batch_id,
            "compute_status": "completed",
        }

    except Exception as e:
        import_service.update_compute_status(batch_id, "failed")
        raise

    finally:
        db.close()
