#!/usr/bin/env python3
"""
Initialize test users and subscription plans in production database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.subscription import Plan
from datetime import datetime


def init_test_users(db):
    """Initialize test users with different roles"""
    print("=" * 60)
    print("初始化测试用户")
    print("=" * 60)

    # Check if VIP user already exists
    vip_user = db.query(User).filter(User.username == "vip_user").first()
    if not vip_user:
        vip_user = User(
            username="vip_user",
            email="vip@qwquant.com",
            password_hash=get_password_hash("vip123456"),
            phone="13800138001",
            role=UserRole.VIP,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(vip_user)
        print("✅ 创建VIP用户: vip_user (密码: vip123456)")
    else:
        print("⏭️  VIP用户已存在，跳过")

    # Check if normal user already exists
    normal_user = db.query(User).filter(User.username == "normal_user").first()
    if not normal_user:
        normal_user = User(
            username="normal_user",
            email="user@qwquant.com",
            password_hash=get_password_hash("user123456"),
            phone="13800138002",
            role=UserRole.NORMAL,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(normal_user)
        print("✅ 创建普通用户: normal_user (密码: user123456)")
    else:
        print("⏭️  普通用户已存在，跳过")

    db.commit()
    print()


def init_subscription_plans(db):
    """Initialize subscription plans"""
    print("=" * 60)
    print("初始化订阅套餐")
    print("=" * 60)

    plans_data = [
        {
            "name": "trial",
            "display_name": "免费试用",
            "description": "7天免费试用，体验基础功能",
            "price": 0.00,
            "original_price": 99.00,
            "duration_days": 7,
            "features": "基础数据查看,每日涨跌榜,概念板块分析",
            "is_active": True,
            "sort_order": 1
        },
        {
            "name": "monthly_vip",
            "display_name": "月度VIP",
            "description": "1个月VIP会员，解锁所有功能",
            "price": 99.00,
            "original_price": 129.00,
            "duration_days": 30,
            "features": "所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析",
            "is_active": True,
            "sort_order": 2
        },
        {
            "name": "quarterly_vip",
            "display_name": "季度VIP",
            "description": "3个月VIP会员，性价比之选",
            "price": 249.00,
            "original_price": 387.00,
            "duration_days": 90,
            "features": "所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析",
            "is_active": True,
            "sort_order": 3
        },
        {
            "name": "yearly_vip",
            "display_name": "年度VIP",
            "description": "12个月VIP会员，最优惠价格",
            "price": 899.00,
            "original_price": 1548.00,
            "duration_days": 365,
            "features": "所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析,专属客服支持,API接口访问",
            "is_active": True,
            "sort_order": 4
        },
        {
            "name": "premium_yearly",
            "display_name": "至尊年费",
            "description": "12个月至尊会员，尊享全部权益",
            "price": 1999.00,
            "original_price": 2999.00,
            "duration_days": 365,
            "features": "所有数据查看,实时涨跌榜,概念板块分析,自选股管理,数据导出,技术指标分析,行业对比分析,专属客服支持,API接口访问,量化策略回测,智能选股推荐,专业研报",
            "is_active": True,
            "sort_order": 5
        }
    ]

    created_count = 0
    for plan_data in plans_data:
        # Check if plan already exists
        existing_plan = db.query(Plan).filter(Plan.name == plan_data["name"]).first()
        if not existing_plan:
            plan = Plan(**plan_data)
            db.add(plan)
            print(f"✅ 创建套餐: {plan_data['display_name']} - ¥{plan_data['price']:.2f}/{plan_data['duration_days']}天")
            created_count += 1
        else:
            print(f"⏭️  套餐已存在，跳过: {plan_data['display_name']}")

    if created_count > 0:
        db.commit()
        print(f"\n✅ 成功创建 {created_count} 个套餐")
    else:
        print("\n⏭️  所有套餐已存在")
    print()


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("生产数据库初始化脚本")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # Initialize test users
        init_test_users(db)

        # Initialize subscription plans
        init_subscription_plans(db)

        # Summary
        total_users = db.query(User).count()
        total_plans = db.query(Plan).count()

        print("=" * 60)
        print("初始化完成")
        print("=" * 60)
        print(f"✅ 用户总数: {total_users}")
        print(f"✅ 套餐总数: {total_plans}")
        print()
        print("测试账号信息:")
        print("  管理员: admin / admin123 (已存在)")
        print("  VIP用户: vip_user / vip123456")
        print("  普通用户: normal_user / user123456")
        print()

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
