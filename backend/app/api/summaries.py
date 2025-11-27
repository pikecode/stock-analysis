"""Summaries API."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock import Concept, ConceptDailySummary
from app.schemas.stock import ConceptSummaryResponse, DailySummaryItem

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.get("/concept/{concept_id}", response_model=ConceptSummaryResponse)
async def get_concept_summary(
    concept_id: int,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    metric_code: str = Query("TTV", description="Metric code"),
    db: Session = Depends(get_db),
):
    """Get concept daily summary (Requirement 2/6)."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    summaries = (
        db.query(ConceptDailySummary)
        .filter(
            ConceptDailySummary.concept_id == concept_id,
            ConceptDailySummary.metric_code == metric_code,
            ConceptDailySummary.trade_date >= start_date,
            ConceptDailySummary.trade_date <= end_date,
        )
        .order_by(ConceptDailySummary.trade_date)
        .all()
    )

    return ConceptSummaryResponse(
        concept_id=concept_id,
        concept_name=concept.concept_name,
        metric_code=metric_code,
        summaries=[
            DailySummaryItem(
                trade_date=s.trade_date,
                total_value=s.total_value or 0,
                avg_value=s.avg_value or 0,
                max_value=s.max_value or 0,
                min_value=s.min_value or 0,
                median_value=s.median_value,
                top10_sum=s.top10_sum,
            )
            for s in summaries
        ],
    )


@router.get("/concept/{concept_id}/compare")
async def compare_metrics(
    concept_id: int,
    trade_date: date = Query(..., description="Trade date"),
    metric_codes: str = Query(None, description="Metric codes (comma-separated)"),
    db: Session = Depends(get_db),
):
    """Compare multiple metrics for a concept on a date."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Build query
    query = db.query(ConceptDailySummary).filter(
        ConceptDailySummary.concept_id == concept_id,
        ConceptDailySummary.trade_date == trade_date,
    )

    if metric_codes:
        codes = [c.strip() for c in metric_codes.split(",")]
        query = query.filter(ConceptDailySummary.metric_code.in_(codes))

    summaries = query.all()

    return {
        "concept_id": concept_id,
        "concept_name": concept.concept_name,
        "trade_date": str(trade_date),
        "metrics": [
            {
                "metric_code": s.metric_code,
                "total_value": s.total_value,
                "avg_value": s.avg_value,
                "max_value": s.max_value,
                "min_value": s.min_value,
            }
            for s in summaries
        ],
    }
