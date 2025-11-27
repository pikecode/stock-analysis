"""Concepts API."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.stock import Concept, Stock, StockConcept, ConceptStockDailyRank
from app.schemas.stock import ConceptResponse, ConceptListResponse, StockResponse

router = APIRouter(prefix="/concepts", tags=["Concepts"])


@router.get("", response_model=ConceptListResponse)
async def list_concepts(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Category filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get concept list."""
    query = db.query(Concept)

    if keyword:
        query = query.filter(Concept.concept_name.ilike(f"%{keyword}%"))

    if category:
        query = query.filter(Concept.category == category)

    total = query.count()
    offset = (page - 1) * page_size
    concepts = query.offset(offset).limit(page_size).all()

    return ConceptListResponse(
        total=total,
        items=[ConceptResponse.model_validate(c) for c in concepts],
    )


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept(concept_id: int, db: Session = Depends(get_db)):
    """Get concept detail."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    return ConceptResponse.model_validate(concept)


@router.get("/{concept_id}/stocks")
async def get_concept_stocks(
    concept_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    trade_date: Optional[date] = Query(None, description="Trade date for metrics (YYYY-MM-DD)"),
    metric_code: str = Query("TTV", description="Metric code (e.g., TTV, EEE)"),
    db: Session = Depends(get_db),
):
    """Get stocks in a concept with optional trade metrics."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Base query - join StockConcept with Stock
    query = (
        db.query(
            Stock.stock_code,
            Stock.stock_name,
            Stock.exchange_prefix,
            ConceptStockDailyRank.trade_value.label("trade_value"),
        )
        .join(
            StockConcept,
            Stock.stock_code == StockConcept.stock_code,
        )
        .filter(StockConcept.concept_id == concept_id)
        .outerjoin(
            ConceptStockDailyRank,
            (ConceptStockDailyRank.concept_id == StockConcept.concept_id)
            & (ConceptStockDailyRank.stock_code == Stock.stock_code)
            & (ConceptStockDailyRank.trade_date == trade_date)
            & (ConceptStockDailyRank.metric_code == metric_code),
        )
    )

    # Get total count
    total = query.count()

    # Order by trade_value descending (highest first), handling None values
    query = query.order_by(ConceptStockDailyRank.trade_value.desc().nullslast())

    # Apply pagination
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    return {
        "concept_id": concept.id,
        "concept_name": concept.concept_name,
        "total": total,
        "trade_date": trade_date,
        "metric_code": metric_code,
        "stocks": [
            {
                "stock_code": r[0],
                "stock_name": r[1],
                "exchange_prefix": r[2],
                "trade_value": r[3],
            }
            for r in results
        ],
    }



@router.get("/{concept_id}/stock-rank-history")
async def get_stock_rank_history(
    concept_id: int,
    stock_code: str = Query(..., description="Stock code to query"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    metric_code: str = Query("TTV", description="Metric code (e.g., TTV, EEE)"),
    db: Session = Depends(get_db),
):
    """Get stock ranking history within a concept over a date range."""
    # Verify concept exists
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Verify stock exists and is in this concept
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    stock_concept = (
        db.query(StockConcept)
        .filter(
            (StockConcept.concept_id == concept_id)
            & (StockConcept.stock_code == stock_code)
        )
        .first()
    )

    if not stock_concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not in concept {concept_id}",
        )

    # Get ranking history for the stock in this concept
    history = (
        db.query(
            ConceptStockDailyRank.trade_date,
            ConceptStockDailyRank.rank,
            ConceptStockDailyRank.trade_value,
        )
        .filter(
            (ConceptStockDailyRank.concept_id == concept_id)
            & (ConceptStockDailyRank.stock_code == stock_code)
            & (ConceptStockDailyRank.metric_code == metric_code)
            & (ConceptStockDailyRank.trade_date >= start_date)
            & (ConceptStockDailyRank.trade_date <= end_date)
        )
        .order_by(ConceptStockDailyRank.trade_date.asc())
        .all()
    )

    return {
        "concept_id": concept.id,
        "concept_name": concept.concept_name,
        "stock_code": stock.stock_code,
        "stock_name": stock.stock_name,
        "metric_code": metric_code,
        "start_date": start_date,
        "end_date": end_date,
        "history": [
            {
                "trade_date": h[0],
                "rank": h[1],
                "trade_value": h[2],
            }
            for h in history
        ],
    }
