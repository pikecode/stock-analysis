"""Data import service.

This module provides the core ImportService class for managing import batches,
metric types, and batch lifecycle operations.

For actual CSV/TXT data parsing and importing, use:
- OptimizedCSVImportService from app.services.optimized_csv_import
- OptimizedTXTImportService from app.services.optimized_txt_import
"""
import hashlib
from datetime import datetime, date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.stock import (
    ImportBatch,
    MetricType,
    StockMetricDataRaw,
)


class ImportService:
    """Service for handling data imports.

    This service manages import batch lifecycle, including:
    - Creating and tracking import batches
    - Managing batch status and metadata
    - Handling metric type lookups
    - Extracting dates from filenames/content
    - Cleaning up old data on re-import

    Note: This service does NOT handle actual data parsing/importing.
    Use OptimizedCSVImportService or OptimizedTXTImportService for that.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_batch(
        self,
        file_name: str,
        file_type: str,
        file_size: int,
        file_content: bytes,
        metric_type_id: Optional[int] = None,
        data_date: Optional[date] = None,
        user_id: Optional[int] = None,
    ) -> ImportBatch:
        """Create an import batch record."""
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check for duplicate - if exists, mark old batch as replaced
        existing = (
            self.db.query(ImportBatch).filter(ImportBatch.file_hash == file_hash).first()
        )
        if existing:
            # Mark existing batch as replaced
            existing.status = "replaced"
            existing.error_message = f"Replaced by new import at {datetime.utcnow()}"
            self.db.flush()

        batch = ImportBatch(
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            metric_type_id=metric_type_id,
            data_date=data_date,
            status="pending",
            created_by=user_id,
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update_batch_status(
        self,
        batch_id: int,
        status: str,
        total_rows: int = 0,
        success_rows: int = 0,
        error_rows: int = 0,
        error_message: Optional[str] = None,
    ):
        """Update batch status."""
        batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if batch:
            batch.status = status
            batch.total_rows = total_rows
            batch.success_rows = success_rows
            batch.error_rows = error_rows
            batch.error_message = error_message
            if status == "processing":
                batch.started_at = datetime.utcnow()
            elif status in ("completed", "failed"):
                batch.completed_at = datetime.utcnow()
            self.db.commit()

    def update_compute_status(self, batch_id: int, status: str):
        """Update computation status."""
        batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if batch:
            batch.compute_status = status
            self.db.commit()

    def delete_old_metric_data(self, metric_type_id: int, data_date: date, exclude_batch_id: int):
        """Delete old metric data for the same metric type and date (for re-import)."""
        # Find old batches with same metric type and date
        old_batches = (
            self.db.query(ImportBatch)
            .filter(
                ImportBatch.metric_type_id == metric_type_id,
                ImportBatch.data_date == data_date,
                ImportBatch.id != exclude_batch_id,
                ImportBatch.status != "replaced",
            )
            .all()
        )

        for old_batch in old_batches:
            # Delete related raw data
            self.db.query(StockMetricDataRaw).filter(
                StockMetricDataRaw.import_batch_id == old_batch.id
            ).delete()

            # Delete related computed rankings
            from app.models.stock import ConceptStockDailyRank, ConceptDailySummary
            self.db.query(ConceptStockDailyRank).filter(
                ConceptStockDailyRank.import_batch_id == old_batch.id
            ).delete()

            # Delete related computed summaries
            self.db.query(ConceptDailySummary).filter(
                ConceptDailySummary.import_batch_id == old_batch.id
            ).delete()

            # Mark old batch as replaced
            old_batch.status = "replaced"
            old_batch.error_message = f"Data replaced by batch {exclude_batch_id}"

        self.db.commit()

    def get_metric_type(self, code: str) -> Optional[MetricType]:
        """Get metric type by code."""
        return self.db.query(MetricType).filter(MetricType.code == code).first()

    def get_metric_type_by_id(self, metric_id: int) -> Optional[MetricType]:
        """Get metric type by ID."""
        return self.db.query(MetricType).filter(MetricType.id == metric_id).first()

    def detect_metric_type(self, file_name: str) -> Optional[MetricType]:
        """Detect metric type from file name."""
        file_name_upper = file_name.upper()
        metric_types = self.db.query(MetricType).filter(MetricType.is_active == True).all()

        for mt in metric_types:
            if mt.code.upper() in file_name_upper:
                return mt
        return None

    def extract_date_from_filename(self, file_name: str) -> Optional[date]:
        """Extract date from filename.

        Supports formats:
        - TTV_20240101.txt -> 2024-01-01
        - TTV_2024-01-01.txt -> 2024-01-01
        - 20240101_TTV.txt -> 2024-01-01
        - 2024-01-01.txt -> 2024-01-01
        """
        import re

        # Try YYYYMMDD format (8 digits)
        match = re.search(r'(\d{8})', file_name)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, '%Y%m%d').date()
            except:
                pass

        # Try YYYY-MM-DD format
        match = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', file_name)
        if match:
            date_str = match.group(1).replace('_', '-')
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                pass

        return None

    def extract_date_from_content(self, file_content: bytes) -> Optional[date]:
        """Extract date from file content (first line, second column)."""
        try:
            # Try UTF-8 first
            content = file_content.decode('utf-8')
        except:
            try:
                # Try GBK
                content = file_content.decode('gbk')
            except:
                return None

        # Get first line
        lines = content.strip().split('\n')
        if not lines:
            return None

        first_line = lines[0].strip()
        if not first_line:
            return None

        # Split by tab or space
        parts = first_line.split('\t') if '\t' in first_line else first_line.split()
        if len(parts) < 2:
            return None

        # Second column should be the date
        date_str = parts[1].strip()

        # Try different date formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue

        return None
