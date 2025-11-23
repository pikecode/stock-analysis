"""Import tasks for Celery."""
import os
from datetime import date

from tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.import_service import ImportService, CSVImportService, TXTImportService
from app.services.compute_service import ComputeService


@celery_app.task(bind=True, name="tasks.process_csv_import")
def process_csv_import(self, batch_id: int, file_path: str):
    """Process CSV file import."""
    db = SessionLocal()
    try:
        import_service = ImportService(db)
        csv_service = CSVImportService(db)

        # Update status
        import_service.update_batch_status(batch_id, "processing")

        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Parse and import
        success_count, error_count = csv_service.parse_and_import(batch_id, file_content)

        # Update status
        import_service.update_batch_status(
            batch_id,
            "completed",
            total_rows=success_count + error_count,
            success_rows=success_count,
            error_rows=error_count,
        )

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
    """Process TXT file import."""
    db = SessionLocal()
    try:
        import_service = ImportService(db)
        txt_service = TXTImportService(db)
        compute_service = ComputeService(db)

        # Update status
        import_service.update_batch_status(batch_id, "processing")

        # Get metric type
        metric_type = import_service.get_metric_type_by_id(metric_type_id)
        if not metric_type:
            raise ValueError(f"Metric type {metric_type_id} not found")

        # Parse data date
        data_date = date.fromisoformat(data_date_str)

        # Delete old data for the same metric type and date
        import_service.delete_old_metric_data(metric_type_id, data_date, batch_id)

        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Parse and import
        success_count, error_count = txt_service.parse_and_import(
            batch_id, file_content, metric_type, data_date
        )

        # Update status
        import_service.update_batch_status(
            batch_id,
            "completed",
            total_rows=success_count + error_count,
            success_rows=success_count,
            error_rows=error_count,
        )

        # Trigger computation
        import_service.update_compute_status(batch_id, "computing")
        compute_service.compute_all_for_batch(batch_id)

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
