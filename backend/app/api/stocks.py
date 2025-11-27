"""Stocks API."""
from __future__ import annotations
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock import Stock, Concept, StockConcept, ConceptStockDailyRank
from app.schemas.stock import (
    StockResponse,
    StockListResponse,
    StockWithConcepts,
    ConceptBrief,
    StockConceptsRankedResponse,
    ConceptRankedItem,
)

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("", response_model=StockListResponse)
async def list_stocks(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    exchange: Optional[str] = Query(None, description="Exchange prefix (SH/SZ/BJ)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
):
    """Get stock list."""
    query = db.query(Stock)

    # Filter by keyword
    if keyword:
        query = query.filter(
            (Stock.stock_code.ilike(f"%{keyword}%"))
            | (Stock.stock_name.ilike(f"%{keyword}%"))
        )

    # Filter by exchange
    if exchange:
        query = query.filter(Stock.exchange_prefix == exchange.upper())

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    stocks = query.offset(offset).limit(page_size).all()

    return StockListResponse(
        total=total,
        items=[StockResponse.model_validate(s) for s in stocks],
    )


@router.get("/{stock_code}", response_model=StockWithConcepts)
async def get_stock(stock_code: str, db: Session = Depends(get_db)):
    """Get stock detail with concepts."""
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    # Get concepts for this stock
    concept_ids = (
        db.query(StockConcept.concept_id)
        .filter(StockConcept.stock_code == stock_code)
        .all()
    )
    concept_ids = [c[0] for c in concept_ids]

    concepts = []
    if concept_ids:
        concepts = db.query(Concept).filter(Concept.id.in_(concept_ids)).all()

    return StockWithConcepts(
        id=stock.id,
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        exchange_prefix=stock.exchange_prefix,
        exchange_name=stock.exchange_name,
        created_at=stock.created_at,
        concepts=[
            ConceptBrief(
                id=c.id,
                concept_name=c.concept_name,
                category=c.category,
            )
            for c in concepts
        ],
    )


@router.get("/{stock_code}/concepts")
async def get_stock_concepts(stock_code: str, db: Session = Depends(get_db)):
    """Get concepts for a stock (Requirement 1)."""
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    # Get concepts
    concept_ids = (
        db.query(StockConcept.concept_id)
        .filter(StockConcept.stock_code == stock_code)
        .all()
    )
    concept_ids = [c[0] for c in concept_ids]

    concepts = []
    if concept_ids:
        concepts = db.query(Concept).filter(Concept.id.in_(concept_ids)).all()

    return {
        "stock_code": stock.stock_code,
        "stock_name": stock.stock_name,
        "concepts": [
            {
                "id": c.id,
                "concept_name": c.concept_name,
                "category": c.category,
            }
            for c in concepts
        ],
    }


@router.get("/{stock_code}/concepts-ranked", response_model=StockConceptsRankedResponse)
async def get_stock_concepts_ranked(
    stock_code: str,
    trade_date: date = Query(..., description="Trade date (YYYY-MM-DD)"),
    metric_code: str = Query("TTV", description="Metric code (e.g., TTV, EEE)"),
    db: Session = Depends(get_db),
):
    """Get concepts for a stock sorted by trade value (high to low).

    Args:
        stock_code: Stock code (e.g., '600000')
        trade_date: Specific trade date to query
        metric_code: Metric code (default: 'TTV')

    Returns:
        Stock info with all concepts sorted by trade_value descending
    """
    # Verify stock exists
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {stock_code} not found",
        )

    # Get stock concepts with ranking data
    # Query: JOIN stock_concepts with ConceptStockDailyRank to get trade_value
    results = (
        db.query(
            Concept.id,
            Concept.concept_name,
            Concept.category,
            ConceptStockDailyRank.trade_value,
            ConceptStockDailyRank.rank,
            ConceptStockDailyRank.percentile,
        )
        .join(
            StockConcept,
            Concept.id == StockConcept.concept_id,
        )
        .outerjoin(
            ConceptStockDailyRank,
            (ConceptStockDailyRank.concept_id == Concept.id)
            & (ConceptStockDailyRank.stock_code == stock_code)
            & (ConceptStockDailyRank.trade_date == trade_date)
            & (ConceptStockDailyRank.metric_code == metric_code),
        )
        .filter(StockConcept.stock_code == stock_code)
        .order_by(ConceptStockDailyRank.trade_value.desc())
        .all()
    )

    # Build response
    concepts = [
        ConceptRankedItem(
            id=r[0],
            concept_name=r[1],
            category=r[2],
            trade_value=r[3],
            rank=r[4],
            percentile=float(r[5]) if r[5] else None,
        )
        for r in results
    ]

    return StockConceptsRankedResponse(
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        exchange_prefix=stock.exchange_prefix,
        trade_date=trade_date,
        metric_code=metric_code,
        total_concepts=len(concepts),
        concepts=concepts,
    )
