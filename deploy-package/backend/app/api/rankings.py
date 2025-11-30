"""Rankings API."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock import (
    Concept,
    Stock,
    ConceptStockDailyRank,
    MetricType,
    StockConcept,
)
from app.schemas.stock import (
    ConceptRankingResponse,
    RankingItem,
    StockRankingHistoryResponse,
    StockRankingHistory,
    TopNCountResponse,
    TopNCountItem,
    ConceptStocksRankingRangeResponse,
    StockRankingInRangeItem,
)

router = APIRouter(prefix="/rankings", tags=["Rankings"])


@router.get("/concept/{concept_id}", response_model=ConceptRankingResponse)
async def get_concept_ranking(
    concept_id: int,
    trade_date: date = Query(..., description="Trade date"),
    metric_code: str = Query("TTV", description="Metric code"),
    limit: int = Query(50, ge=1, le=500, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Get ranking list for a concept on a specific date (Requirement 3)."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Get rankings
    rankings = (
        db.query(ConceptStockDailyRank)
        .filter(
            ConceptStockDailyRank.concept_id == concept_id,
            ConceptStockDailyRank.trade_date == trade_date,
            ConceptStockDailyRank.metric_code == metric_code,
        )
        .order_by(ConceptStockDailyRank.rank)
        .limit(limit)
        .all()
    )

    if not rankings:
        return ConceptRankingResponse(
            concept_id=concept_id,
            concept_name=concept.concept_name,
            trade_date=trade_date,
            metric_code=metric_code,
            rankings=[],
        )

    # Get stock names
    stock_codes = [r.stock_code for r in rankings]
    stocks = db.query(Stock).filter(Stock.stock_code.in_(stock_codes)).all()
    stock_map = {s.stock_code: s.stock_name for s in stocks}

    return ConceptRankingResponse(
        concept_id=concept_id,
        concept_name=concept.concept_name,
        trade_date=trade_date,
        metric_code=metric_code,
        rankings=[
            RankingItem(
                rank=r.rank,
                stock_code=r.stock_code,
                stock_name=stock_map.get(r.stock_code),
                trade_value=r.trade_value,
            )
            for r in rankings
        ],
    )


@router.get("/stock/{stock_code}", response_model=StockRankingHistoryResponse)
async def get_stock_ranking_history(
    stock_code: str,
    concept_id: int = Query(..., description="Concept ID"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    metric_code: str = Query("TTV", description="Metric code"),
    db: Session = Depends(get_db),
):
    """Get stock ranking history in a concept (Requirement 5/6)."""
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Get ranking history
    history = (
        db.query(ConceptStockDailyRank)
        .filter(
            ConceptStockDailyRank.stock_code == stock_code,
            ConceptStockDailyRank.concept_id == concept_id,
            ConceptStockDailyRank.metric_code == metric_code,
            ConceptStockDailyRank.trade_date >= start_date,
            ConceptStockDailyRank.trade_date <= end_date,
        )
        .order_by(ConceptStockDailyRank.trade_date)
        .all()
    )

    return StockRankingHistoryResponse(
        stock_code=stock_code,
        stock_name=stock.stock_name,
        concept_id=concept_id,
        concept_name=concept.concept_name,
        metric_code=metric_code,
        history=[
            StockRankingHistory(
                trade_date=h.trade_date,
                rank=h.rank,
                trade_value=h.trade_value,
            )
            for h in history
        ],
    )


@router.get("/stock/{stock_code}/top-n-count", response_model=TopNCountResponse)
async def get_top_n_count(
    stock_code: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    top_n: int = Query(10, ge=1, le=100, description="Top N threshold"),
    concept_id: Optional[int] = Query(None, description="Concept ID (optional)"),
    metric_code: str = Query("TTV", description="Metric code"),
    db: Session = Depends(get_db),
):
    """Get count of times stock appeared in top N (Requirement 4)."""
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    # Build query
    query = db.query(
        ConceptStockDailyRank.concept_id,
        func.count().label("top_n_count"),
    ).filter(
        ConceptStockDailyRank.stock_code == stock_code,
        ConceptStockDailyRank.metric_code == metric_code,
        ConceptStockDailyRank.trade_date >= start_date,
        ConceptStockDailyRank.trade_date <= end_date,
        ConceptStockDailyRank.rank <= top_n,
    )

    if concept_id:
        query = query.filter(ConceptStockDailyRank.concept_id == concept_id)

    query = query.group_by(ConceptStockDailyRank.concept_id)
    results = query.all()

    # Count total trading days
    trading_days = (
        db.query(func.count(func.distinct(ConceptStockDailyRank.trade_date)))
        .filter(
            ConceptStockDailyRank.stock_code == stock_code,
            ConceptStockDailyRank.metric_code == metric_code,
            ConceptStockDailyRank.trade_date >= start_date,
            ConceptStockDailyRank.trade_date <= end_date,
        )
        .scalar()
    ) or 0

    # Get concept names
    concept_ids = [r[0] for r in results]
    concepts = {}
    if concept_ids:
        concept_list = db.query(Concept).filter(Concept.id.in_(concept_ids)).all()
        concepts = {c.id: c.concept_name for c in concept_list}

    statistics = [
        TopNCountItem(
            concept_id=r[0],
            concept_name=concepts.get(r[0], "Unknown"),
            top_n_count=r[1],
            top_n_rate=round(r[1] / trading_days * 100, 2) if trading_days > 0 else 0,
        )
        for r in results
    ]

    # Sort by count descending
    statistics.sort(key=lambda x: x.top_n_count, reverse=True)

    return TopNCountResponse(
        stock_code=stock_code,
        stock_name=stock.stock_name,
        date_range={"start": str(start_date), "end": str(end_date)},
        top_n=top_n,
        metric_code=metric_code,
        trading_days=trading_days,
        statistics=statistics,
    )


@router.get("/concept/{concept_id}/stocks-in-range", response_model=ConceptStocksRankingRangeResponse)
async def get_concept_stocks_in_date_range(
    concept_id: int,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    metric_code: str = Query("TTV", description="Metric code"),
    limit: int = Query(100, ge=1, le=500, description="Number of results"),
    use_latest_date: bool = Query(True, description="Use latest date in range if True"),
    db: Session = Depends(get_db),
):
    """Get stocks ranking in a concept within a date range.

    Args:
        concept_id: Concept ID
        start_date: Start date of the range
        end_date: End date of the range
        metric_code: Metric code (e.g., TTV, EEE)
        limit: Max number of stocks to return
        use_latest_date: If True, returns ranking for the latest date in range.
                        If False, returns for each date in range.

    Returns:
        Stocks ranking in the concept within date range, sorted by trade_value (high to low)
    """
    # Verify concept exists
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    if use_latest_date:
        # Find latest date in range
        latest_date = (
            db.query(func.max(ConceptStockDailyRank.trade_date))
            .filter(
                ConceptStockDailyRank.concept_id == concept_id,
                ConceptStockDailyRank.metric_code == metric_code,
                ConceptStockDailyRank.trade_date >= start_date,
                ConceptStockDailyRank.trade_date <= end_date,
            )
            .scalar()
        )

        if not latest_date:
            return ConceptStocksRankingRangeResponse(
                concept_id=concept_id,
                concept_name=concept.concept_name,
                metric_code=metric_code,
                start_date=start_date,
                end_date=end_date,
                query_date=None,
                stocks=[],
            )

        # Get rankings for latest date
        rankings = (
            db.query(ConceptStockDailyRank)
            .filter(
                ConceptStockDailyRank.concept_id == concept_id,
                ConceptStockDailyRank.trade_date == latest_date,
                ConceptStockDailyRank.metric_code == metric_code,
            )
            .order_by(ConceptStockDailyRank.trade_value.desc())
            .limit(limit)
            .all()
        )

        # Get stock names
        stock_codes = [r.stock_code for r in rankings]
        stocks = db.query(Stock).filter(Stock.stock_code.in_(stock_codes)).all()
        stock_map = {s.stock_code: s.stock_name for s in stocks}

        return ConceptStocksRankingRangeResponse(
            concept_id=concept_id,
            concept_name=concept.concept_name,
            metric_code=metric_code,
            start_date=start_date,
            end_date=end_date,
            query_date=latest_date,
            stocks=[
                StockRankingInRangeItem(
                    stock_code=r.stock_code,
                    stock_name=stock_map.get(r.stock_code),
                    rank=r.rank,
                    trade_value=r.trade_value,
                    trade_date=r.trade_date,
                )
                for r in rankings
            ],
        )
    else:
        # Get all rankings in date range, grouped by stock and aggregated
        # This returns average rank and total trade_value for each stock in the range
        rankings = (
            db.query(
                ConceptStockDailyRank.stock_code,
                func.avg(ConceptStockDailyRank.trade_value).label("avg_trade_value"),
                func.max(ConceptStockDailyRank.trade_value).label("max_trade_value"),
                func.min(ConceptStockDailyRank.rank).label("best_rank"),
                func.avg(ConceptStockDailyRank.rank).label("avg_rank"),
                func.count(func.distinct(ConceptStockDailyRank.trade_date)).label("trading_days"),
            )
            .filter(
                ConceptStockDailyRank.concept_id == concept_id,
                ConceptStockDailyRank.metric_code == metric_code,
                ConceptStockDailyRank.trade_date >= start_date,
                ConceptStockDailyRank.trade_date <= end_date,
            )
            .group_by(ConceptStockDailyRank.stock_code)
            .order_by(func.avg(ConceptStockDailyRank.trade_value).desc())
            .limit(limit)
            .all()
        )

        if not rankings:
            return ConceptStocksRankingRangeResponse(
                concept_id=concept_id,
                concept_name=concept.concept_name,
                metric_code=metric_code,
                start_date=start_date,
                end_date=end_date,
                query_date=None,
                stocks=[],
            )

        # Get stock names
        stock_codes = [r[0] for r in rankings]
        stocks = db.query(Stock).filter(Stock.stock_code.in_(stock_codes)).all()
        stock_map = {s.stock_code: s.stock_name for s in stocks}

        return ConceptStocksRankingRangeResponse(
            concept_id=concept_id,
            concept_name=concept.concept_name,
            metric_code=metric_code,
            start_date=start_date,
            end_date=end_date,
            query_date=None,
            stocks=[
                StockRankingInRangeItem(
                    stock_code=r[0],
                    stock_name=stock_map.get(r[0]),
                    rank=int(r[3]) if r[3] else None,  # best_rank
                    trade_value=int(r[1]) if r[1] else 0,  # avg_trade_value
                    trade_date=None,
                )
                for r in rankings
            ],
        )
