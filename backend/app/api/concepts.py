"""Concepts API."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock import Concept, Stock, StockConcept
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
    db: Session = Depends(get_db),
):
    """Get stocks in a concept."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Get stock codes
    stock_codes_query = db.query(StockConcept.stock_code).filter(
        StockConcept.concept_id == concept_id
    )
    total = stock_codes_query.count()

    offset = (page - 1) * page_size
    stock_codes = stock_codes_query.offset(offset).limit(page_size).all()
    stock_codes = [s[0] for s in stock_codes]

    # Get stock info
    stocks = []
    if stock_codes:
        stocks = db.query(Stock).filter(Stock.stock_code.in_(stock_codes)).all()

    return {
        "concept_id": concept.id,
        "concept_name": concept.concept_name,
        "total": total,
        "stocks": [
            {
                "stock_code": s.stock_code,
                "stock_name": s.stock_name,
                "exchange_prefix": s.exchange_prefix,
            }
            for s in stocks
        ],
    }
