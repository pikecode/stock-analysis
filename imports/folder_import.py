#!/usr/bin/env python
"""
文件夹批量导入脚本 - 自动扫描并导入文件夹下的所有TXT文件

Usage:
    python imports/folder_import.py <folder_path> [options]

Examples:
    # 导入文件夹下所有TXT文件
    python imports/folder_import.py test-data

    # 只导入EEE指标
    python imports/folder_import.py test-data --metric-code EEE

    # 只导入特定日期范围
    python imports/folder_import.py test-data --start-date 2025-11-18 --end-date 2025-11-21

    # 并行处理（4个进程）
    python imports/folder_import.py test-data --parallel 4

    # 跳过已导入的文件
    python imports/folder_import.py test-data --skip-existing
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import argparse
import re
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
import logging
from tqdm import tqdm

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.services.import_service import ImportService
from app.models.stock import ImportBatch

# 创建数据库会话
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    file_path: str
    file_name: str
    metric_code: str
    data_date: date
    file_size: int

    def __str__(self):
        return f"{self.metric_code}_{self.data_date.strftime('%Y-%m-%d')}"


class FolderImporter:
    """文件夹批量导入器"""

    # 支持的文件名格式
    # EEE_2025-11-18.txt
    # TTV_20251118.txt
    # EEE_2025_11_18.txt
    FILE_PATTERNS = [
        r'([A-Z]+)_(\d{4}-\d{2}-\d{2})\.txt$',  # METRIC_YYYY-MM-DD.txt
        r'([A-Z]+)_(\d{8})\.txt$',               # METRIC_YYYYMMDD.txt
        r'([A-Z]+)_(\d{4})_(\d{2})_(\d{2})\.txt$',  # METRIC_YYYY_MM_DD.txt
    ]

    def __init__(
        self,
        folder_path: str,
        metric_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        parallel: int = 1,
        skip_existing: bool = False
    ):
        self.folder_path = Path(folder_path)
        self.metric_code = metric_code.upper() if metric_code else None
        self.start_date = start_date
        self.end_date = end_date
        self.parallel = max(1, min(parallel, cpu_count()))
        self.skip_existing = skip_existing

        if not self.folder_path.exists():
            raise ValueError(f"文件夹不存在: {folder_path}")

    def parse_filename(self, file_name: str) -> Optional[Tuple[str, date]]:
        """从文件名解析指标代码和日期"""
        for pattern in self.FILE_PATTERNS:
            match = re.match(pattern, file_name)
            if match:
                metric = match.group(1).upper()

                # 解析日期
                if len(match.groups()) == 2:
                    date_str = match.group(2)
                    if len(date_str) == 8:  # YYYYMMDD
                        data_date = datetime.strptime(date_str, '%Y%m%d').date()
                    else:  # YYYY-MM-DD
                        data_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:  # YYYY_MM_DD
                    year, month, day = match.group(2), match.group(3), match.group(4)
                    data_date = date(int(year), int(month), int(day))

                return metric, data_date

        return None

    def scan_folder(self) -> List[FileInfo]:
        """扫描文件夹，获取所有符合条件的TXT文件"""
        logger.info(f"扫描文件夹: {self.folder_path}")

        files = []
        skipped = 0

        for file_path in self.folder_path.glob("*.txt"):
            # 跳过混合日期文件
            if 'mixed' in file_path.name.lower():
                continue

            # 解析文件名
            parsed = self.parse_filename(file_path.name)
            if not parsed:
                logger.warning(f"无法解析文件名: {file_path.name}")
                skipped += 1
                continue

            metric_code, data_date = parsed

            # 过滤指标
            if self.metric_code and metric_code != self.metric_code:
                continue

            # 过滤日期范围
            date_str = data_date.strftime('%Y-%m-%d')
            if self.start_date and date_str < self.start_date:
                continue
            if self.end_date and date_str > self.end_date:
                continue

            # 创建文件信息
            file_info = FileInfo(
                file_path=str(file_path),
                file_name=file_path.name,
                metric_code=metric_code,
                data_date=data_date,
                file_size=file_path.stat().st_size
            )
            files.append(file_info)

        logger.info(f"找到 {len(files)} 个文件，跳过 {skipped} 个")
        return sorted(files, key=lambda x: (x.metric_code, x.data_date))

    def check_existing(self, file_info: FileInfo) -> bool:
        """检查文件是否已导入"""
        db = SessionLocal()
        try:
            # 查找同名文件的成功导入记录
            existing = db.query(ImportBatch).filter(
                ImportBatch.file_name == file_info.file_name,
                ImportBatch.status == 'completed',
                ImportBatch.error_rows == 0
            ).first()
            return existing is not None
        finally:
            db.close()

    def import_single_file(self, file_info: FileInfo) -> Tuple[str, bool, str]:
        """导入单个文件"""
        try:
            # 读取文件内容
            with open(file_info.file_path, 'rb') as f:
                file_content = f.read()

            # 创建新的数据库会话
            db = SessionLocal()

            try:
                # 获取导入服务
                import_service = ImportService(db)

                # 获取或创建指标类型
                metric_type = import_service.get_metric_type(file_info.metric_code)
                if not metric_type:
                    from app.models.stock import MetricType
                    metric_type = MetricType(
                        code=file_info.metric_code,
                        name=file_info.metric_code,
                        description=f"{file_info.metric_code} 交易数据"
                    )
                    db.add(metric_type)
                    db.commit()
                    db.refresh(metric_type)

                # 创建导入批次
                batch = import_service.create_batch(
                    file_name=file_info.file_name,
                    file_type='TXT',
                    file_size=file_info.file_size,
                    file_content=file_content,
                    metric_type_id=metric_type.id,
                    data_date=file_info.data_date,
                    user_id=1
                )

                # 保存batch_id（在session关闭前）
                batch_id = batch.id

                # 调用统一导入方法
                success_count, error_count = import_service.import_txt_file(
                    batch_id=batch_id,
                    file_content=file_content,
                    metric_type_id=metric_type.id,
                    data_date=file_info.data_date
                )

                db.close()

                return (
                    str(file_info),
                    True,
                    f"成功: {success_count}条, 批次ID: {batch_id}"
                )

            except Exception as e:
                db.close()
                raise e

        except Exception as e:
            logger.error(f"导入失败 {file_info}: {str(e)}")
            return str(file_info), False, f"失败: {str(e)}"

    def import_folder(self):
        """执行文件夹批量导入"""

        # 扫描文件
        files = self.scan_folder()

        if not files:
            logger.info("没有找到符合条件的文件")
            return

        # 检查已存在的文件
        if self.skip_existing:
            original_count = len(files)
            files = [f for f in files if not self.check_existing(f)]
            skipped_count = original_count - len(files)
            if skipped_count > 0:
                logger.info(f"跳过已导入的文件: {skipped_count} 个")

        if not files:
            logger.info("所有文件都已导入")
            return

        # 显示统计
        print("\n" + "="*60)
        print("📊 文件夹导入统计:")
        print(f"  文件夹: {self.folder_path}")
        print(f"  待导入文件数: {len(files)}")

        # 按指标统计
        metric_stats = {}
        for f in files:
            metric_stats[f.metric_code] = metric_stats.get(f.metric_code, 0) + 1

        print(f"  指标分布:")
        for metric, count in sorted(metric_stats.items()):
            print(f"    - {metric}: {count} 个文件")

        print(f"  并行进程数: {self.parallel}")
        print("="*60 + "\n")

        # 执行导入
        start_time = datetime.now()
        success_count = 0
        failed_count = 0
        results = []

        with tqdm(total=len(files), desc="导入进度") as pbar:
            if self.parallel == 1:
                # 单进程
                for file_info in files:
                    name, success, msg = self.import_single_file(file_info)
                    results.append((name, success, msg))

                    if success:
                        success_count += 1
                    else:
                        failed_count += 1

                    pbar.set_postfix_str(f"{name}: {msg[:30]}...")
                    pbar.update(1)
            else:
                # 多进程
                with Pool(processes=self.parallel) as pool:
                    for name, success, msg in pool.imap_unordered(
                        self.import_single_file, files
                    ):
                        results.append((name, success, msg))

                        if success:
                            success_count += 1
                        else:
                            failed_count += 1

                        pbar.set_postfix_str(f"{name}: {msg[:30]}...")
                        pbar.update(1)

        end_time = datetime.now()

        # 显示结果
        print("\n" + "="*60)
        print("✅ 导入完成:")
        print(f"  成功: {success_count}/{len(files)}")
        print(f"  失败: {failed_count}")
        print(f"  耗时: {end_time - start_time}")

        if failed_count > 0:
            print("\n❌ 失败的文件:")
            for name, success, msg in results:
                if not success:
                    print(f"    - {name}: {msg}")

        print("="*60 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量导入文件夹下的所有TXT文件'
    )

    parser.add_argument('folder', help='文件夹路径')
    parser.add_argument('--metric-code', help='只导入指定指标（如EEE）')
    parser.add_argument('--start-date', help='开始日期（YYYY-MM-DD）')
    parser.add_argument('--end-date', help='结束日期（YYYY-MM-DD）')
    parser.add_argument('--parallel', type=int, default=1, help='并行进程数（默认1）')
    parser.add_argument('--skip-existing', action='store_true', help='跳过已导入的文件')

    args = parser.parse_args()

    # 创建导入器
    importer = FolderImporter(
        folder_path=args.folder,
        metric_code=args.metric_code,
        start_date=args.start_date,
        end_date=args.end_date,
        parallel=args.parallel,
        skip_existing=args.skip_existing
    )

    try:
        # 执行导入
        importer.import_folder()
    except KeyboardInterrupt:
        print("\n⚠️ 导入被中断")
    except Exception as e:
        logger.error(f"导入失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
