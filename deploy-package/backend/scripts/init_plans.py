#!/usr/bin/env python3
"""Initialize default subscription plans."""
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.subscription import Plan


def init_plans():
    """Create default subscription plans."""
    db = SessionLocal()

    try:
        # Check if plans already exist
        existing_plans = db.query(Plan).count()
        if existing_plans > 0:
            print(f"Plans already exist: {existing_plans} plans found")
            return

        # Create default plans
        plans = [
            Plan(
                name='monthly',
                display_name='月度套餐',
                description='月度订阅，享受所有报表和分析功能，随时取消无合同约束',
                price=Decimal('99.00'),
                original_price=Decimal('129.00'),
                duration_days=30,
                features='["daily_reports", "concept_analysis", "stock_ranking", "portfolio_analysis"]',
                is_active=True,
                sort_order=1,
            ),
            Plan(
                name='quarterly',
                display_name='季度套餐',
                description='季度订阅，相比月度套餐优惠15%，更经济实惠',
                price=Decimal('249.00'),
                original_price=Decimal('349.00'),
                duration_days=90,
                features='["daily_reports", "concept_analysis", "stock_ranking", "portfolio_analysis", "performance_metrics"]',
                is_active=True,
                sort_order=2,
            ),
            Plan(
                name='semi_annual',
                display_name='半年度套餐',
                description='半年订阅，相比月度套餐优惠22%，享受持续的数据更新和分析',
                price=Decimal('579.00'),
                original_price=Decimal('749.00'),
                duration_days=180,
                features='["daily_reports", "concept_analysis", "stock_ranking", "portfolio_analysis", "performance_metrics", "export_data"]',
                is_active=True,
                sort_order=3,
            ),
            Plan(
                name='yearly',
                display_name='年度套餐',
                description='年度订阅，相比月度套餐优惠33%，折扣力度最大，最划算的选择',
                price=Decimal('699.00'),
                original_price=Decimal('1000.00'),
                duration_days=365,
                features='["daily_reports", "concept_analysis", "stock_ranking", "portfolio_analysis", "performance_metrics", "export_data", "api_access"]',
                is_active=True,
                sort_order=4,
            ),
        ]

        # Add all plans to database
        for plan in plans:
            db.add(plan)

        db.commit()
        print(f"✅ Successfully created {len(plans)} default plans:")
        for plan in plans:
            print(f"  - {plan.display_name} ({plan.name}): ¥{plan.price}/month, {plan.duration_days} days")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating plans: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    init_plans()
