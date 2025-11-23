"""Stock and concept models."""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
    Date,
    Boolean,
    ForeignKey,
    Numeric,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class MetricType(Base):
    """Metric type configuration."""

    __tablename__ = "metric_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    file_pattern = Column(String(100))
    field_mapping = Column(JSON, default={})
    rank_order = Column(String(10), default="DESC")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Stock(Base):
    """Stock information."""

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), unique=True, nullable=False, index=True)
    stock_name = Column(String(100))
    exchange_prefix = Column(String(10), index=True)  # SH, SZ, BJ
    exchange_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    concepts = relationship(
        "Concept", secondary="stock_concepts", back_populates="stocks"
    )


class Concept(Base):
    """Concept/sector information."""

    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    concept_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stocks = relationship(
        "Stock", secondary="stock_concepts", back_populates="concepts"
    )


class StockConcept(Base):
    """Stock-Concept relationship."""

    __tablename__ = "stock_concepts"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Industry(Base):
    """Industry information."""

    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    industry_name = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("industries.id"))
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class StockIndustry(Base):
    """Stock-Industry relationship."""

    __tablename__ = "stock_industries"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    industry_id = Column(
        Integer, ForeignKey("industries.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)


class ImportBatch(Base):
    """Import batch record."""

    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # CSV, TXT
    metric_type_id = Column(Integer, ForeignKey("metric_types.id"))
    file_size = Column(BigInteger)
    file_hash = Column(String(64), index=True)
    data_date = Column(Date, index=True)
    status = Column(String(20), default="pending", index=True)
    total_rows = Column(Integer, default=0)
    success_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    compute_status = Column(String(20), default="pending")
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)

    # Relationships
    metric_type = relationship("MetricType")


class StockMetricDataRaw(Base):
    """Raw metric data from TXT files."""

    __tablename__ = "stock_metric_data_raw"

    id = Column(BigInteger, primary_key=True, index=True)
    import_batch_id = Column(
        Integer, ForeignKey("import_batches.id"), nullable=False, index=True
    )
    metric_type_id = Column(
        Integer, ForeignKey("metric_types.id"), nullable=False, index=True
    )
    metric_code = Column(String(50), nullable=False)
    stock_code_raw = Column(String(30), nullable=False)
    stock_code = Column(String(20), nullable=False, index=True)
    exchange_prefix = Column(String(10))
    trade_date = Column(Date, nullable=False, index=True)
    trade_value = Column(BigInteger, nullable=False)
    source_row_number = Column(Integer)
    raw_line = Column(Text)
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConceptStockDailyRank(Base):
    """Pre-computed daily ranking."""

    __tablename__ = "concept_stock_daily_rank"

    id = Column(BigInteger, primary_key=True, index=True)
    metric_type_id = Column(Integer, ForeignKey("metric_types.id"), nullable=False)
    metric_code = Column(String(50), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    stock_code = Column(String(20), nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    trade_value = Column(BigInteger, nullable=False)
    rank = Column(Integer, nullable=False)
    total_stocks = Column(Integer)
    percentile = Column(Numeric(5, 2))
    computed_at = Column(DateTime, default=datetime.utcnow)
    import_batch_id = Column(Integer, ForeignKey("import_batches.id"))


class ConceptDailySummary(Base):
    """Pre-computed daily summary."""

    __tablename__ = "concept_daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    metric_type_id = Column(Integer, ForeignKey("metric_types.id"), nullable=False)
    metric_code = Column(String(50), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    total_value = Column(BigInteger)
    avg_value = Column(BigInteger)
    max_value = Column(BigInteger)
    min_value = Column(BigInteger)
    stock_count = Column(Integer)
    median_value = Column(BigInteger)
    top10_sum = Column(BigInteger)
    computed_at = Column(DateTime, default=datetime.utcnow)
    import_batch_id = Column(Integer, ForeignKey("import_batches.id"))
