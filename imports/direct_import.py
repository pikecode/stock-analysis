#!/usr/bin/env python
"""直接导入脚本 - 命令行导入数据，无需API"""
import sys
import argparse
from datetime import date
from pathlib import Path

# 添加项目路径
# 脚本位置: imports/direct_import.py -> 项目根 -> backend
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.services.import_service import ImportService
from app.services.optimized_csv_import import OptimizedCSVImportService
from app.services.optimized_txt_import import OptimizedTXTImportService
from app.services.compute_service import ComputeService


def main():
    parser = argparse.ArgumentParser(description="直接导入数据文件")
    parser.add_argument("file_path", type=str, help="文件路径")
    parser.add_argument("--type", required=True, choices=["CSV", "TXT"],
                        help="文件类型")
    parser.add_argument("--metric-code", type=str, help="指标代码（TXT文件必需）")
    parser.add_argument("--date", type=str, help="数据日期，格式YYYY-MM-DD（TXT文件）")
    parser.add_argument("--user-id", type=int, default=1, help="用户ID，默认为1")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 验证文件存在
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"❌ 错误：文件不存在 {args.file_path}")
        sys.exit(1)

    # 读取文件内容
    with open(file_path, "rb") as f:
        file_content = f.read()

    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 创建导入批次
        import_service = ImportService(db)
        metric_type_id = None

        if args.type == "TXT":
            # TXT文件需要指标和日期
            if not args.metric_code:
                print("❌ 错误：TXT文件必须指定 --metric-code")
                sys.exit(1)

            if args.date:
                try:
                    parsed_date = date.fromisoformat(args.date)
                except ValueError:
                    print(f"❌ 错误：日期格式不正确 {args.date}，应为 YYYY-MM-DD")
                    sys.exit(1)
            else:
                # 尝试从文件名提取日期
                parsed_date = import_service.extract_date_from_filename(file_path.name)
                if not parsed_date:
                    parsed_date = import_service.extract_date_from_content(file_content)
                if not parsed_date:
                    print("❌ 错误：无法从文件提取日期，请使用 --date 参数")
                    sys.exit(1)

            # 获取指标类型
            metric_type = import_service.get_metric_type(args.metric_code.upper())
            if not metric_type:
                print(f"❌ 错误：未知的指标代码 {args.metric_code}")
                sys.exit(1)

            metric_type_id = metric_type.id

        # 创建批次
        batch = import_service.create_batch(
            file_name=file_path.name,
            file_type=args.type,
            file_size=len(file_content),
            file_content=file_content,
            metric_type_id=metric_type_id,
            data_date=parsed_date if args.type == "TXT" else None,
            user_id=args.user_id
        )

        if args.verbose:
            print(f"✓ 创建批次: {batch.id}")

        # 调用统一导入方法
        if args.type == "CSV":
            print("📥 导入CSV文件（股票-概念映射）...")
            success, errors = import_service.import_csv_file(batch.id, file_content)

            print(f"✓ CSV导入完成")
            print(f"  - 成功: {success} 条")
            print(f"  - 错误: {errors} 条")

        else:  # TXT
            print(f"📥 导入TXT文件（{args.metric_code}交易数据）...")
            success, errors = import_service.import_txt_file(
                batch.id,
                file_content,
                metric_type_id,
                parsed_date
            )

            print(f"✓ TXT导入完成")
            print(f"  - 成功: {success} 条")
            print(f"  - 错误: {errors} 条")
            print(f"  - 已自动计算排名和汇总统计")

        print(f"\n✅ 导入成功（批次ID: {batch.id}）")

    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
