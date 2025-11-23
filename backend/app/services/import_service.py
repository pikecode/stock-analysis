"""Data import service."""
import hashlib
import os
from datetime import datetime, date
from typing import Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.models.stock import (
    ImportBatch,
    MetricType,
    Stock,
    Concept,
    StockConcept,
    StockMetricDataRaw,
)


class ImportService:
    """Service for handling data imports."""

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


class CSVImportService:
    """Service for importing CSV files (stock-concept mapping)."""

    def __init__(self, db: Session):
        self.db = db

    def parse_and_import(self, batch_id: int, file_content: bytes) -> Tuple[int, int]:
        """Parse CSV and import stock-concept mappings."""
        try:
            # Read CSV
            from io import BytesIO
            df = pd.read_csv(BytesIO(file_content), encoding="utf-8", dtype=str)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        # Detect columns
        columns = df.columns.tolist()
        stock_code_col = self._find_column(columns, ["股票代码", "code", "stock_code", "代码"])
        stock_name_col = self._find_column(columns, ["股票名称", "name", "stock_name", "名称"])
        concept_col = self._find_column(columns, ["概念", "concept", "板块", "concept_name"])

        if stock_code_col is None:
            raise ValueError("Cannot find stock code column")

        # Prepare data for batch insert
        stocks_data = []
        concepts_data = []
        stock_concepts_data = []
        raw_data = []

        success_count = 0
        error_count = 0

        for idx, row in df.iterrows():
            try:
                stock_code = str(row[stock_code_col]).strip()
                if not stock_code or stock_code == "nan":
                    continue

                stock_name = str(row[stock_name_col]).strip() if stock_name_col else None
                if stock_name == "nan":
                    stock_name = None

                concept_name = str(row[concept_col]).strip() if concept_col else None
                if concept_name == "nan":
                    concept_name = None

                # Collect stock data
                stocks_data.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                })

                # Collect concept data
                if concept_name:
                    concepts_data.append({
                        'concept_name': concept_name,
                    })
                    stock_concepts_data.append({
                        'stock_code': stock_code,
                        'concept_name': concept_name,
                    })

                # Collect raw data for archiving
                raw_data.append({
                    'batch_id': batch_id,
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'concept_name': concept_name,
                    'row_number': idx + 1,
                })

                success_count += 1
            except Exception as e:
                error_count += 1
                continue

        # Batch insert using raw SQL for better performance
        self._batch_insert_raw_data(raw_data)
        self._batch_insert_stocks(stocks_data)
        self._batch_insert_concepts(concepts_data)
        self._batch_insert_stock_concepts(stock_concepts_data)

        self.db.commit()
        return success_count, error_count

    def _find_column(self, columns: list, candidates: list) -> Optional[str]:
        """Find column name from candidates."""
        for col in columns:
            col_lower = col.lower().strip()
            for candidate in candidates:
                if candidate.lower() in col_lower:
                    return col
        return None

    def _batch_insert_raw_data(self, raw_data: list):
        """Batch insert raw CSV data for archiving."""
        if not raw_data:
            return

        # Prepare values for SQL
        values = []
        for item in raw_data:
            batch_id = item['batch_id']
            stock_code = item['stock_code'].replace("'", "''") if item['stock_code'] else ''
            stock_name = item['stock_name'].replace("'", "''") if item['stock_name'] else None
            concept_name = item['concept_name'].replace("'", "''") if item['concept_name'] else None
            row_number = item['row_number']

            stock_name_str = f"'{stock_name}'" if stock_name else 'NULL'
            concept_name_str = f"'{concept_name}'" if concept_name else 'NULL'

            values.append(f"({batch_id}, '{stock_code}', {stock_name_str}, {concept_name_str}, {row_number})")

        if values:
            # Batch insert in chunks of 1000 to avoid SQL size limits
            chunk_size = 1000
            for i in range(0, len(values), chunk_size):
                chunk = values[i:i + chunk_size]
                sql = f"""
                    INSERT INTO stock_concept_mapping_raw
                    (import_batch_id, stock_code, stock_name, concept_name, source_row_number)
                    VALUES {','.join(chunk)}
                """
                self.db.execute(text(sql))

    def _batch_insert_stocks(self, stocks_data: list):
        """Batch insert stocks using ON CONFLICT."""
        if not stocks_data:
            return

        # Remove duplicates within the batch
        seen = {}
        unique_stocks = []
        for item in stocks_data:
            code = item['stock_code']
            if code not in seen:
                seen[code] = item
                unique_stocks.append(item)
            elif item.get('stock_name') and not seen[code].get('stock_name'):
                # Update with name if we have it
                seen[code]['stock_name'] = item['stock_name']

        # Prepare values for SQL
        values = []
        for item in unique_stocks:
            stock_code = item['stock_code'].replace("'", "''")
            stock_name = item['stock_name'].replace("'", "''") if item['stock_name'] else None
            if stock_name:
                values.append(f"('{stock_code}', '{stock_name}')")
            else:
                values.append(f"('{stock_code}', NULL)")

        if values:
            sql = f"""
                INSERT INTO stocks (stock_code, stock_name)
                VALUES {','.join(values)}
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = COALESCE(EXCLUDED.stock_name, stocks.stock_name)
            """
            self.db.execute(text(sql))

    def _batch_insert_concepts(self, concepts_data: list):
        """Batch insert concepts using ON CONFLICT."""
        if not concepts_data:
            return

        # Remove duplicates
        unique_concepts = list({item['concept_name']: item for item in concepts_data}.values())

        # Prepare values for SQL
        values = []
        for item in unique_concepts:
            concept_name = item['concept_name'].replace("'", "''")
            values.append(f"('{concept_name}')")

        if values:
            sql = f"""
                INSERT INTO concepts (concept_name)
                VALUES {','.join(values)}
                ON CONFLICT (concept_name) DO NOTHING
            """
            self.db.execute(text(sql))

    def _batch_insert_stock_concepts(self, stock_concepts_data: list):
        """Batch insert stock-concept relationships."""
        if not stock_concepts_data:
            return

        # Remove duplicates
        seen = set()
        unique_relations = []
        for item in stock_concepts_data:
            key = (item['stock_code'], item['concept_name'])
            if key not in seen:
                seen.add(key)
                unique_relations.append(item)

        # First, get concept IDs
        concept_names = list(set(item['concept_name'] for item in unique_relations))
        concept_map = {}
        for name in concept_names:
            concept = self.db.query(Concept).filter(Concept.concept_name == name).first()
            if concept:
                concept_map[name] = concept.id

        # Prepare values for SQL
        values = []
        for item in unique_relations:
            concept_id = concept_map.get(item['concept_name'])
            if concept_id:
                stock_code = item['stock_code'].replace("'", "''")
                values.append(f"('{stock_code}', {concept_id})")

        if values:
            sql = f"""
                INSERT INTO stock_concepts (stock_code, concept_id)
                VALUES {','.join(values)}
                ON CONFLICT (stock_code, concept_id) DO NOTHING
            """
            self.db.execute(text(sql))


class TXTImportService:
    """Service for importing TXT files (metric data)."""

    def __init__(self, db: Session):
        self.db = db

    def parse_and_import(
        self,
        batch_id: int,
        file_content: bytes,
        metric_type: MetricType,
        data_date: date,
    ) -> Tuple[int, int]:
        """Parse TXT and import metric data."""
        try:
            content = file_content.decode("utf-8")
        except:
            content = file_content.decode("gbk")

        lines = content.strip().split("\n")
        success_count = 0
        error_count = 0

        # Pre-load all stock codes that have concepts (performance optimization)
        stocks_with_concepts = set(
            sc.stock_code for sc in
            self.db.query(StockConcept.stock_code).distinct().all()
        )

        for line_num, line in enumerate(lines, 1):
            try:
                line = line.strip()
                if not line:
                    continue

                # Parse line (tab or space separated)
                parts = line.split("\t") if "\t" in line else line.split()
                if len(parts) < 3:
                    error_count += 1
                    continue

                stock_code_raw = parts[0].strip()
                trade_date_str = parts[1].strip()
                trade_value_str = parts[2].strip()

                # Parse stock code (separate prefix)
                stock_code, exchange_prefix = self._parse_stock_code(stock_code_raw)

                # Parse date
                trade_date = self._parse_date(trade_date_str, data_date)

                # Parse value
                trade_value = int(float(trade_value_str))

                # Check if stock has concepts (using pre-loaded set)
                has_concept = stock_code in stocks_with_concepts

                # Create raw data record
                raw_data = StockMetricDataRaw(
                    import_batch_id=batch_id,
                    metric_type_id=metric_type.id,
                    metric_code=metric_type.code,
                    stock_code_raw=stock_code_raw,
                    stock_code=stock_code,
                    exchange_prefix=exchange_prefix,
                    trade_date=trade_date,
                    trade_value=trade_value,
                    source_row_number=line_num,
                    raw_line=line,
                    is_valid=has_concept,  # 只有有概念的股票才标记为有效
                )
                self.db.add(raw_data)

                # Ensure stock exists
                self._ensure_stock(stock_code, exchange_prefix)

                if has_concept:
                    success_count += 1
                else:
                    error_count += 1  # 没有概念的算作错误

                # Batch commit
                if success_count % 1000 == 0:
                    self.db.flush()

            except Exception as e:
                error_count += 1
                continue

        self.db.commit()
        return success_count, error_count

    def _parse_stock_code(self, raw_code: str) -> Tuple[str, Optional[str]]:
        """Parse stock code and extract prefix."""
        raw_code = raw_code.upper().strip()

        # Check for known prefixes
        if raw_code.startswith(("SH", "SZ", "BJ")):
            prefix = raw_code[:2]
            code = raw_code[2:]
            return code, prefix

        # No prefix
        return raw_code, None

    def _parse_date(self, date_str: str, default_date: date) -> date:
        """Parse date string."""
        if not date_str or date_str == "nan":
            return default_date

        # Try different formats
        for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue

        return default_date

    def _ensure_stock(self, stock_code: str, exchange_prefix: Optional[str] = None):
        """Ensure stock exists."""
        stock = self.db.query(Stock).filter(Stock.stock_code == stock_code).first()
        if not stock:
            exchange_name = None
            if exchange_prefix == "SH":
                exchange_name = "上海证券交易所"
            elif exchange_prefix == "SZ":
                exchange_name = "深圳证券交易所"
            elif exchange_prefix == "BJ":
                exchange_name = "北京证券交易所"

            stock = Stock(
                stock_code=stock_code,
                exchange_prefix=exchange_prefix,
                exchange_name=exchange_name,
            )
            self.db.add(stock)
