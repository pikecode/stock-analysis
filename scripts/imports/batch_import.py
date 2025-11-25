#!/usr/bin/env python
"""
批量导入脚本 - 支持大文件自动拆分和并行处理
Usage:
    python scripts/batch_import.py <file> --type TXT --metric-code <code> [options]

Examples:
    # 基础用法
    python scripts/batch_import.py /path/to/EEE.txt --type TXT --metric-code EEE

    # 并行处理
    python scripts/batch_import.py /path/to/EEE.txt --type TXT --metric-code EEE --parallel 4

    # 从指定日期继续
    python scripts/batch_import.py /path/to/EEE.txt --type TXT --metric-code EEE --resume-from 2024-01-01

    # 只处理特定日期范围
    python scripts/batch_import.py /path/to/EEE.txt --type TXT --metric-code EEE --start-date 2024-01-01 --end-date 2024-12-31
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Set
import argparse
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import multiprocessing as mp
from multiprocessing import Pool, Queue, Manager
import logging
from tqdm import tqdm
import hashlib
import tempfile
import signal
import atexit

# 添加项目路径
# 脚本位置: scripts/imports/batch_import.py
# 需要访问: backend/app/...
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.services.optimized_txt_import import OptimizedTXTImportService
from app.models.stock import ImportBatch, MetricType

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
class DateBatch:
    """日期批次数据"""
    trade_date: str
    lines: List[str]
    count: int


@dataclass
class ImportProgress:
    """导入进度记录"""
    file_path: str
    file_hash: str
    total_dates: int
    processed_dates: Set[str]
    failed_dates: Set[str]
    start_time: str
    last_update: str

    def to_dict(self):
        """转换为可JSON序列化的字典"""
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'total_dates': self.total_dates,
            'processed_dates': list(self.processed_dates),
            'failed_dates': list(self.failed_dates),
            'start_time': self.start_time,
            'last_update': self.last_update
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典恢复"""
        return cls(
            file_path=data['file_path'],
            file_hash=data['file_hash'],
            total_dates=data['total_dates'],
            processed_dates=set(data.get('processed_dates', [])),
            failed_dates=set(data.get('failed_dates', [])),
            start_time=data['start_time'],
            last_update=data['last_update']
        )


class BatchImporter:
    """批量导入器"""

    def __init__(self, metric_code: str, parallel: int = 1):
        self.metric_code = metric_code
        self.parallel = max(1, min(parallel, mp.cpu_count()))
        self.progress_file = f"/tmp/batch_import_{metric_code}.json"
        self.temp_dir = tempfile.mkdtemp(prefix=f"batch_import_{metric_code}_")
        self.progress = None

        # 注册清理函数
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def cleanup(self):
        """清理临时文件"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _handle_interrupt(self, signum, frame):
        """处理中断信号"""
        logger.info("接收到中断信号，保存进度...")
        if self.progress:
            self.save_progress()
        self.cleanup()
        sys.exit(0)

    def get_file_hash(self, file_path: str, sample_size: int = 1024*1024) -> str:
        """获取文件哈希（基于文件头部采样）"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read(sample_size))
        return hasher.hexdigest()

    def load_progress(self, file_path: str) -> Optional[ImportProgress]:
        """加载进度记录"""
        if not os.path.exists(self.progress_file):
            return None

        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
            progress = ImportProgress.from_dict(data)

            # 验证文件哈希
            current_hash = self.get_file_hash(file_path)
            if progress.file_hash != current_hash:
                logger.warning("文件已变更，重新开始导入")
                return None

            return progress
        except Exception as e:
            logger.error(f"加载进度失败: {e}")
            return None

    def save_progress(self):
        """保存进度"""
        if not self.progress:
            return

        try:
            self.progress.last_update = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"保存进度失败: {e}")

    def scan_file(self, file_path: str) -> Dict[str, DateBatch]:
        """扫描文件，按日期分组"""
        logger.info(f"开始扫描文件: {file_path}")

        date_batches = defaultdict(list)
        line_count = 0

        # 自动检测编码
        encodings = ['utf-8', 'gbk', 'gb2312']
        content = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.readlines()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError(f"无法解析文件编码: {file_path}")

        # 分组数据
        with tqdm(total=len(content), desc="扫描文件") as pbar:
            for line in content:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('\t') if '\t' in line else line.split()
                if len(parts) >= 3:
                    trade_date = parts[1]
                    date_batches[trade_date].append(line)
                    line_count += 1

                pbar.update(1)

        # 转换为DateBatch对象
        result = {}
        for trade_date, lines in date_batches.items():
            result[trade_date] = DateBatch(
                trade_date=trade_date,
                lines=lines,
                count=len(lines)
            )

        logger.info(f"扫描完成: {len(result)}个日期, {line_count}条数据")
        return result

    def save_date_batch(self, date_batch: DateBatch) -> str:
        """保存单个日期批次到临时文件"""
        temp_file = os.path.join(self.temp_dir, f"{self.metric_code}_{date_batch.trade_date}.txt")

        with open(temp_file, 'w', encoding='utf-8') as f:
            for line in date_batch.lines:
                f.write(line + '\n')

        return temp_file

    def import_single_date(self, args: Tuple[str, str, str, int]) -> Tuple[str, bool, str]:
        """导入单个日期的数据（用于多进程）"""
        trade_date_str, temp_file, metric_code, metric_type_id = args

        try:
            # 创建新的数据库会话
            db = SessionLocal()

            # 解析日期
            trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()

            # 读取临时文件
            with open(temp_file, 'rb') as f:
                file_content = f.read()

            # 创建导入批次
            import_batch = ImportBatch(
                file_name=f"{metric_code}_{trade_date_str}.txt",
                file_type='TXT',
                file_size=len(file_content),
                file_hash=hashlib.md5(file_content).hexdigest(),
                total_rows=0,
                success_rows=0,
                error_rows=0,
                status='processing',
                created_by=1
            )
            db.add(import_batch)
            db.commit()

            # 执行导入
            service = OptimizedTXTImportService(db)
            success_count, error_count = service.parse_and_import_with_compute(
                batch_id=import_batch.id,
                file_content=file_content,
                metric_type_id=metric_type_id,
                metric_code=metric_code,
                data_date=trade_date
            )

            # 更新批次状态
            import_batch.status = 'completed'
            import_batch.success_rows = success_count
            import_batch.error_rows = error_count
            import_batch.total_rows = success_count + error_count
            import_batch.completed_at = datetime.now()
            db.commit()

            db.close()

            return trade_date_str, True, f"成功: {success_count}条"

        except Exception as e:
            logger.error(f"导入失败 {trade_date_str}: {str(e)}")
            return trade_date_str, False, f"失败: {str(e)}"

    def run_parallel_import(
        self,
        date_batches: Dict[str, DateBatch],
        metric_type_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """并行执行导入"""

        # 过滤日期范围
        dates_to_process = []
        for trade_date, batch in date_batches.items():
            # 跳过已处理的
            if self.progress and trade_date in self.progress.processed_dates:
                continue

            # 检查日期范围
            if start_date and trade_date < start_date:
                continue
            if end_date and trade_date > end_date:
                continue

            dates_to_process.append((trade_date, batch))

        if not dates_to_process:
            logger.info("没有需要处理的日期")
            return

        # 排序
        dates_to_process.sort(key=lambda x: x[0])

        logger.info(f"准备处理 {len(dates_to_process)} 个日期，使用 {self.parallel} 个进程")

        # 准备任务
        tasks = []
        for trade_date, batch in dates_to_process:
            temp_file = self.save_date_batch(batch)
            tasks.append((trade_date, temp_file, self.metric_code, metric_type_id))

        # 创建进度条
        with tqdm(total=len(tasks), desc="导入进度") as pbar:
            if self.parallel == 1:
                # 单进程
                for task in tasks:
                    trade_date, success, msg = self.import_single_date(task)

                    if success:
                        self.progress.processed_dates.add(trade_date)
                    else:
                        self.progress.failed_dates.add(trade_date)

                    pbar.set_postfix_str(f"{trade_date}: {msg}")
                    pbar.update(1)
                    self.save_progress()
            else:
                # 多进程
                with Pool(processes=self.parallel) as pool:
                    # 使用imap_unordered获取结果
                    for trade_date, success, msg in pool.imap_unordered(
                        self.import_single_date, tasks
                    ):
                        if success:
                            self.progress.processed_dates.add(trade_date)
                        else:
                            self.progress.failed_dates.add(trade_date)

                        pbar.set_postfix_str(f"{trade_date}: {msg}")
                        pbar.update(1)
                        self.save_progress()

    def import_file(
        self,
        file_path: str,
        resume: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """执行文件导入"""

        # 获取metric_type_id
        db = SessionLocal()
        metric_type = db.query(MetricType).filter_by(code=self.metric_code).first()
        if not metric_type:
            # 创建新的指标类型
            metric_type = MetricType(
                code=self.metric_code,
                name=self.metric_code,
                description=f"{self.metric_code} 交易数据"
            )
            db.add(metric_type)
            db.commit()

        metric_type_id = metric_type.id
        db.close()

        # 加载或创建进度
        if resume:
            self.progress = self.load_progress(file_path)

        if not self.progress:
            self.progress = ImportProgress(
                file_path=file_path,
                file_hash=self.get_file_hash(file_path),
                total_dates=0,
                processed_dates=set(),
                failed_dates=set(),
                start_time=datetime.now().isoformat(),
                last_update=datetime.now().isoformat()
            )

        # 扫描文件
        date_batches = self.scan_file(file_path)
        self.progress.total_dates = len(date_batches)

        # 显示统计
        print("\n" + "="*60)
        print("📊 文件统计:")
        print(f"  总日期数: {len(date_batches)}")
        print(f"  总数据量: {sum(b.count for b in date_batches.values())}")
        print(f"  已处理: {len(self.progress.processed_dates)}")
        print(f"  失败: {len(self.progress.failed_dates)}")

        if self.progress.processed_dates:
            print(f"  继续从: {min(self.progress.processed_dates)}")

        print("="*60 + "\n")

        # 执行导入
        start_time = datetime.now()
        self.run_parallel_import(date_batches, metric_type_id, start_date, end_date)
        end_time = datetime.now()

        # 显示结果
        print("\n" + "="*60)
        print("✅ 导入完成:")
        print(f"  成功: {len(self.progress.processed_dates)}/{self.progress.total_dates}")
        print(f"  失败: {len(self.progress.failed_dates)}")
        print(f"  耗时: {end_time - start_time}")

        if self.progress.failed_dates:
            print("\n❌ 失败的日期:")
            for date in sorted(self.progress.failed_dates)[:10]:
                print(f"    - {date}")
            if len(self.progress.failed_dates) > 10:
                print(f"    ... 还有 {len(self.progress.failed_dates) - 10} 个")

        print("="*60 + "\n")

        # 清理进度文件（如果全部完成）
        if len(self.progress.processed_dates) == self.progress.total_dates:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
                print("✨ 进度文件已清理")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量导入TXT文件 - 支持大文件自动拆分和并行处理'
    )

    parser.add_argument('file', help='要导入的文件路径')
    parser.add_argument('--type', choices=['TXT'], default='TXT', help='文件类型')
    parser.add_argument('--metric-code', required=True, help='指标代码（如EEE）')
    parser.add_argument('--parallel', type=int, default=4, help='并行进程数（默认4）')
    parser.add_argument('--resume', action='store_true', help='从上次中断处继续')
    parser.add_argument('--start-date', help='开始日期（YYYY-MM-DD）')
    parser.add_argument('--end-date', help='结束日期（YYYY-MM-DD）')

    args = parser.parse_args()

    # 验证文件
    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)

    # 创建导入器
    importer = BatchImporter(
        metric_code=args.metric_code,
        parallel=args.parallel
    )

    try:
        # 执行导入
        importer.import_file(
            file_path=args.file,
            resume=args.resume,
            start_date=args.start_date,
            end_date=args.end_date
        )
    except KeyboardInterrupt:
        print("\n⚠️ 导入被中断")
    except Exception as e:
        logger.error(f"导入失败: {e}", exc_info=True)
        sys.exit(1)
    finally:
        importer.cleanup()


if __name__ == '__main__':
    main()