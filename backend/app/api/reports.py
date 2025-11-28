"""Reports API."""
from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.models.stock import Concept, Stock, StockConcept, ConceptDailySummary, ConceptStockDailyRank

router = APIRouter(prefix="/reports", tags=["Reports"])


class StockInNewHigh(BaseModel):
    code: str
    name: str
    trade_value: float
    price_change_pct: float
    rank: int


class ConceptNewHigh(BaseModel):
    concept_id: int
    concept_name: str
    total_trade_value: float
    daily_rank: int
    is_new_high: bool
    stocks: List[StockInNewHigh]


@router.get("/concept-new-highs", response_model=List[ConceptNewHigh])
async def get_concept_new_highs(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Get concepts that reached new highs on the last day of the date range.

    Logic:
    1. For each concept, get all daily summaries within the date range
    2. Require at least 2 days of data (last day must have something to compare against)
    3. Verify that the last record's date matches end_date exactly
    4. Compare last day's volume against all previous days in the range
    5. If last day > max(previous days), it's a new high concept
    6. Return those concepts sorted by trading volume on the last day

    Requirements:
    - Must have data on end_date (if no data on that day, concept is skipped)
    - Last day volume must be STRICTLY GREATER than all previous days
    - Requires at least 2 days of data to qualify as new high

    Args:
        start_date: Start date for the analysis period (YYYY-MM-DD)
        end_date: End date for the analysis period - last day checked for new highs (YYYY-MM-DD)
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date",
        )

    # Get all concepts
    concepts = db.query(Concept).all()
    results = []

    for concept in concepts:
        # Get daily summaries for this concept within the date range
        summaries = (
            db.query(ConceptDailySummary)
            .filter(
                and_(
                    ConceptDailySummary.concept_id == concept.id,
                    ConceptDailySummary.trade_date >= start,
                    ConceptDailySummary.trade_date <= end,
                )
            )
            .order_by(ConceptDailySummary.trade_date)
            .all()
        )

        # Need at least 2 days of data to compare (last day vs previous days)
        if len(summaries) < 2:
            continue

        # Get the last day's summary
        last_day_summary = summaries[-1]

        # Verify that the last day is exactly end_date
        # If end_date has no data, skip this concept
        if last_day_summary.trade_date != end:
            continue

        last_day_value = last_day_summary.total_value or 0

        if last_day_value == 0:
            continue

        # Calculate the maximum value from previous days (excluding last day)
        previous_max = max(
            (summary.total_value or 0) for summary in summaries[:-1]
        )

        # Check if last day is strictly greater than all previous days (new high)
        if last_day_value <= previous_max:
            continue

        # Get stocks in this concept for the last day, sorted by trade value
        stock_rank_data_list = (
            db.query(ConceptStockDailyRank)
            .filter(
                and_(
                    ConceptStockDailyRank.concept_id == concept.id,
                    ConceptStockDailyRank.trade_date == end,
                )
            )
            .order_by(ConceptStockDailyRank.trade_value.desc())
            .all()
        )

        stocks = []
        for stock_rank_data in stock_rank_data_list:
            # Get stock name from Stock table
            stock = db.query(Stock).filter(Stock.stock_code == stock_rank_data.stock_code).first()
            stock_name = stock.stock_name if stock else stock_rank_data.stock_code

            stocks.append(
                StockInNewHigh(
                    code=stock_rank_data.stock_code,
                    name=stock_name,
                    trade_value=stock_rank_data.trade_value or 0,
                    price_change_pct=0,  # ConceptStockDailyRank doesn't have price_change_pct
                    rank=stock_rank_data.rank or 0,
                )
            )

        results.append(
            ConceptNewHigh(
                concept_id=concept.id,
                concept_name=concept.concept_name,
                total_trade_value=last_day_value,
                daily_rank=0,
                is_new_high=True,
                stocks=stocks,
            )
        )

    # Sort by trade value descending
    results.sort(key=lambda x: x.total_trade_value, reverse=True)

    return results


@router.get("/concept-trend/{concept_id}")
async def get_concept_trend(
    concept_id: int,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Get daily trading volume trend for a concept within date range.

    Used for displaying trend chart when clicking on a concept.
    Returns daily aggregated trade values and marks the final day (end_date).
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date",
        )

    summaries = (
        db.query(ConceptDailySummary)
        .filter(
            and_(
                ConceptDailySummary.concept_id == concept_id,
                ConceptDailySummary.trade_date >= start,
                ConceptDailySummary.trade_date <= end,
            )
        )
        .order_by(ConceptDailySummary.trade_date)
        .all()
    )

    return [
        {
            "date": summary.trade_date.isoformat(),
            "trade_value": summary.total_value or 0,
            "is_peak": summary.trade_date == end,  # Mark the last day (new high day)
        }
        for summary in summaries
    ]
