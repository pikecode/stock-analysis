"""Stocks API."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock import Stock, Concept, StockConcept
from app.schemas.stock import (
    StockResponse,
    StockListResponse,
    StockWithConcepts,
    ConceptBrief,
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
