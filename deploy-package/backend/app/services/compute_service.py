"""Computation service for rankings and summaries."""
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.stock import ImportBatch


class ComputeService:
    """Service for computing rankings and summaries."""

    def __init__(self, db: Session):
        self.db = db

    def compute_all_for_batch(self, batch_id: int):
        """Recompute rankings and summaries for a batch based on existing raw data.

        This method:
        1. Clears previous computation results for this batch
        2. Recomputes rankings and summaries from scratch using the existing raw data
        3. Updates the batch status
        """
        # Update status
        batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")

        batch.compute_status = "computing"
        self.db.commit()

        try:
            # Clear previous computation results for this batch
            self._clear_previous_results(batch_id)

            # Recompute rankings from raw data
            self.compute_rankings(batch_id)

            # Recompute summaries from raw data
            self.compute_summaries(batch_id)

            # Update status
            batch.compute_status = "completed"
            self.db.commit()

        except Exception as e:
            batch.compute_status = "failed"
            batch.error_message = str(e)
            self.db.commit()
            raise

    def _clear_previous_results(self, batch_id: int):
        """Clear previous computation results for this batch."""
        # Delete from concept_daily_summary
        sql_summary = text("""
            DELETE FROM concept_daily_summary
            WHERE import_batch_id = :batch_id
        """)
        self.db.execute(sql_summary, {"batch_id": batch_id})

        # Delete from concept_stock_daily_rank
        sql_rank = text("""
            DELETE FROM concept_stock_daily_rank
            WHERE import_batch_id = :batch_id
        """)
        self.db.execute(sql_rank, {"batch_id": batch_id})

        self.db.commit()

    def compute_rankings(self, batch_id: int):
        """Compute stock rankings within concepts from raw data.

        Calculates DENSE_RANK for each stock within its concepts for each trade date.
        """
        sql = text("""
            INSERT INTO concept_stock_daily_rank (
                metric_type_id, metric_code, concept_id, stock_code, trade_date,
                trade_value, rank, import_batch_id
            )
            SELECT
                r.metric_type_id,
                r.metric_code,
                sc.concept_id,
                r.stock_code,
                r.trade_date,
                r.trade_value,
                DENSE_RANK() OVER (
                    PARTITION BY r.metric_type_id, sc.concept_id, r.trade_date
                    ORDER BY r.trade_value DESC
                ) as rank,
                :batch_id as import_batch_id
            FROM stock_metric_data_raw r
            JOIN stock_concepts sc ON r.stock_code = sc.stock_code
            WHERE r.import_batch_id = :batch_id
              AND r.is_valid = true
        """)

        self.db.execute(sql, {"batch_id": batch_id})
        self.db.commit()

    def compute_summaries(self, batch_id: int):
        """Compute concept daily summaries from raw data.

        Calculates aggregated statistics (total, avg, max, min, median) for each concept on each date.
        """
        sql = text("""
            INSERT INTO concept_daily_summary (
                metric_type_id, metric_code, concept_id, trade_date,
                total_value, avg_value, max_value, min_value,
                median_value, import_batch_id
            )
            SELECT
                r.metric_type_id,
                r.metric_code,
                sc.concept_id,
                r.trade_date,
                SUM(r.trade_value) as total_value,
                AVG(r.trade_value)::BIGINT as avg_value,
                MAX(r.trade_value) as max_value,
                MIN(r.trade_value) as min_value,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.trade_value)::BIGINT as median_value,
                :batch_id as import_batch_id
            FROM stock_metric_data_raw r
            JOIN stock_concepts sc ON r.stock_code = sc.stock_code
            WHERE r.import_batch_id = :batch_id
              AND r.is_valid = true
            GROUP BY r.metric_type_id, r.metric_code, sc.concept_id, r.trade_date
        """)

        self.db.execute(sql, {"batch_id": batch_id})
        self.db.commit()

