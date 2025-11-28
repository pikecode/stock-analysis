"""Plans API."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.subscription import Plan
from app.models.user import User
from app.schemas.subscription import (
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=List[PlanResponse])
async def list_active_plans(
    db: Session = Depends(get_db),
):
    """Get all active plans (public endpoint)."""
    plans = db.query(Plan).filter(Plan.is_active == True).order_by(Plan.sort_order).all()
    return plans


@router.get("/admin/all", response_model=List[PlanResponse])
async def list_all_plans(
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get all plans including inactive ones (admin only)."""
    plans = db.query(Plan).order_by(Plan.sort_order).all()
    return plans


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
):
    """Get plan by ID (public endpoint)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return plan


@router.post("/admin", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan: PlanCreate,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Create a new plan (admin only)."""
    # Check if plan name already exists
    existing = db.query(Plan).filter(Plan.name == plan.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan with this name already exists",
        )

    db_plan = Plan(
        name=plan.name,
        display_name=plan.display_name,
        description=plan.description,
        price=plan.price,
        original_price=plan.original_price,
        duration_days=plan.duration_days,
        features=plan.features,
        is_active=plan.is_active,
        sort_order=plan.sort_order,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.put("/admin/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan: PlanUpdate,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Update plan (admin only)."""
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    # Update fields
    update_data = plan.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan, field, value)

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.delete("/admin/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Delete plan (admin only)."""
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    db.delete(db_plan)
    db.commit()
