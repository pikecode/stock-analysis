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
        """Compute rankings and summaries for a batch."""
        # Update status
        batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")

        batch.compute_status = "computing"
        self.db.commit()

        try:
            # Compute rankings
            self.compute_rankings(batch_id)

            # Compute summaries
            self.compute_summaries(batch_id)

            # Update status
            batch.compute_status = "completed"
            self.db.commit()

        except Exception as e:
            batch.compute_status = "failed"
            batch.error_message = str(e)
            self.db.commit()
            raise

    def compute_rankings(self, batch_id: int):
        """Compute stock rankings within concepts."""
        sql = text("""
            INSERT INTO concept_stock_daily_rank (
                metric_type_id, metric_code, concept_id, stock_code, trade_date,
                trade_value, rank, total_stocks, percentile, import_batch_id
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
                COUNT(*) OVER (
                    PARTITION BY r.metric_type_id, sc.concept_id, r.trade_date
                ) as total_stocks,
                ROUND(
                    100.0 * (1 - (DENSE_RANK() OVER (
                        PARTITION BY r.metric_type_id, sc.concept_id, r.trade_date
                        ORDER BY r.trade_value DESC
                    ) - 1)::DECIMAL / NULLIF(COUNT(*) OVER (
                        PARTITION BY r.metric_type_id, sc.concept_id, r.trade_date
                    ), 0)), 2
                ) as percentile,
                :batch_id as import_batch_id
            FROM stock_metric_data_raw r
            JOIN stock_concepts sc ON r.stock_code = sc.stock_code
            WHERE r.import_batch_id = :batch_id
              AND r.is_valid = true
            ON CONFLICT (metric_type_id, concept_id, stock_code, trade_date)
            DO UPDATE SET
                trade_value = EXCLUDED.trade_value,
                rank = EXCLUDED.rank,
                total_stocks = EXCLUDED.total_stocks,
                percentile = EXCLUDED.percentile,
                computed_at = CURRENT_TIMESTAMP,
                import_batch_id = EXCLUDED.import_batch_id
        """)

        self.db.execute(sql, {"batch_id": batch_id})
        self.db.commit()

    def compute_summaries(self, batch_id: int):
        """Compute concept daily summaries."""
        sql = text("""
            INSERT INTO concept_daily_summary (
                metric_type_id, metric_code, concept_id, trade_date,
                total_value, avg_value, max_value, min_value, stock_count,
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
                COUNT(*) as stock_count,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.trade_value)::BIGINT as median_value,
                :batch_id as import_batch_id
            FROM stock_metric_data_raw r
            JOIN stock_concepts sc ON r.stock_code = sc.stock_code
            WHERE r.import_batch_id = :batch_id
              AND r.is_valid = true
            GROUP BY r.metric_type_id, r.metric_code, sc.concept_id, r.trade_date
            ON CONFLICT (metric_type_id, concept_id, trade_date)
            DO UPDATE SET
                total_value = EXCLUDED.total_value,
                avg_value = EXCLUDED.avg_value,
                max_value = EXCLUDED.max_value,
                min_value = EXCLUDED.min_value,
                stock_count = EXCLUDED.stock_count,
                median_value = EXCLUDED.median_value,
                computed_at = CURRENT_TIMESTAMP,
                import_batch_id = EXCLUDED.import_batch_id
        """)

        self.db.execute(sql, {"batch_id": batch_id})
        self.db.commit()

        # Compute top10_sum separately
        self._compute_top10_sum(batch_id)

    def _compute_top10_sum(self, batch_id: int):
        """Compute top 10 sum for each concept."""
        sql = text("""
            UPDATE concept_daily_summary s
            SET top10_sum = (
                SELECT COALESCE(SUM(sub.trade_value), 0)
                FROM (
                    SELECT r.trade_value
                    FROM stock_metric_data_raw r
                    JOIN stock_concepts sc ON r.stock_code = sc.stock_code
                    WHERE sc.concept_id = s.concept_id
                      AND r.trade_date = s.trade_date
                      AND r.metric_type_id = s.metric_type_id
                      AND r.is_valid = true
                    ORDER BY r.trade_value DESC
                    LIMIT 10
                ) sub
            )
            WHERE s.import_batch_id = :batch_id
        """)

        self.db.execute(sql, {"batch_id": batch_id})
        self.db.commit()
