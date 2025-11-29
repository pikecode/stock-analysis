"""Stock and concept schemas."""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# Concept schemas (defined first for dependencies)
class ConceptBase(BaseModel):
    """Base concept schema."""

    concept_name: str
    category: Optional[str] = None


class ConceptBrief(BaseModel):
    """Brief concept info."""

    id: int
    concept_name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class ConceptResponse(ConceptBase):
    """Concept response schema."""

    id: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Stock schemas
class StockBase(BaseModel):
    """Base stock schema."""

    stock_code: str
    stock_name: Optional[str] = None
    exchange_prefix: Optional[str] = None


class StockResponse(StockBase):
    """Stock response schema."""

    id: int
    exchange_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockListResponse(BaseModel):
    """Stock list response."""

    total: int
    items: list[StockWithConcepts]


class StockWithConcepts(StockResponse):
    """Stock with concepts."""

    concepts: list[ConceptBrief] = []


class ConceptListResponse(BaseModel):
    """Concept list response."""

    total: int
    items: list[ConceptResponse]


# Ranking schemas
class RankingItem(BaseModel):
    """Single ranking item."""

    rank: int
    stock_code: str
    stock_name: Optional[str] = None
    trade_value: int


class ConceptRankingResponse(BaseModel):
    """Concept ranking response."""

    concept_id: int
    concept_name: str
    trade_date: date
    metric_code: str
    rankings: list[RankingItem]


class StockRankingHistory(BaseModel):
    """Stock ranking history item."""

    trade_date: date
    rank: int
    trade_value: int


class StockRankingHistoryResponse(BaseModel):
    """Stock ranking history response."""

    stock_code: str
    stock_name: Optional[str] = None
    concept_id: int
    concept_name: str
    metric_code: str
    history: list[StockRankingHistory]


class TopNCountItem(BaseModel):
    """Top N count item."""

    concept_id: int
    concept_name: str
    top_n_count: int
    top_n_rate: float


class TopNCountResponse(BaseModel):
    """Top N count response."""

    stock_code: str
    stock_name: Optional[str] = None
    date_range: dict
    top_n: int
    metric_code: str
    trading_days: int
    statistics: list[TopNCountItem]


# Summary schemas
class DailySummaryItem(BaseModel):
    """Daily summary item."""

    trade_date: date
    total_value: int
    avg_value: int
    max_value: int
    min_value: int
    median_value: Optional[int] = None
    top10_sum: Optional[int] = None


class ConceptSummaryResponse(BaseModel):
    """Concept summary response."""

    concept_id: int
    concept_name: str
    metric_code: str
    summaries: list[DailySummaryItem]


# Metric schemas
class MetricTypeResponse(BaseModel):
    """Metric type response."""

    id: int
    code: str
    name: str
    file_pattern: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# Import schemas
class ImportBatchResponse(BaseModel):
    """Import batch response."""

    id: int
    file_name: str
    file_type: str
    metric_code: Optional[str] = None
    data_date: Optional[date] = None
    status: str
    compute_status: str
    total_rows: int
    success_rows: int
    error_rows: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImportUploadResponse(BaseModel):
    """Import upload response."""

    batch_id: int
    file_name: str
    status: str
    message: str


# Stock with ranked concepts schemas
class ConceptRankedItem(BaseModel):
    """Concept with ranking info."""

    id: int
    concept_name: str
    category: Optional[str] = None
    trade_value: Optional[int] = None
    rank: Optional[int] = None
    concept_total_value: Optional[int] = None
    concept_stock_count: Optional[int] = None
    concept_avg_value: Optional[float] = None


class StockConceptsRankedResponse(BaseModel):
    """Stock with ranked concepts response."""

    stock_code: str
    stock_name: str
    exchange_prefix: Optional[str] = None
    trade_date: date
    metric_code: str
    total_concepts: int
    concepts: list[ConceptRankedItem]


# Concept stocks in date range schemas
class StockRankingInRangeItem(BaseModel):
    """Stock ranking in a concept within date range."""

    stock_code: str
    stock_name: Optional[str] = None
    rank: int
    trade_value: int
    trade_date: Optional[date] = None


class ConceptStocksRankingRangeResponse(BaseModel):
    """Concept stocks ranking in date range response."""

    concept_id: int
    concept_name: str
    metric_code: str
    start_date: date
    end_date: date
    query_date: Optional[date] = None  # 实际查询的日期（如果使用latest_date）
    stocks: list[StockRankingInRangeItem]
