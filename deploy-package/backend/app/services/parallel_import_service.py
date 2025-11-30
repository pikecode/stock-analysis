"""并行导入服务 - 处理大文件"""
import concurrent.futures
from typing import List, Tuple, Optional
from dataclasses import dataclass
import threading
from queue import Queue
import logging
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ChunkResult:
    """块处理结果"""
    chunk_id: int
    success_count: int
    error_count: int
    data: List


class ParallelTXTImportService:
    """并行处理大文件的TXT导入服务"""

    def __init__(self, db_session_factory: sessionmaker):
        """
        使用session factory而不是单个session，因为需要多线程处理
        """
        self.db_session_factory = db_session_factory
        self.results_queue = Queue()

    def process_large_file(
        self,
        file_content: bytes,
        batch_id: int,
        metric_type_id: int,
        metric_code: str,
        data_date,
        num_workers: int = 4
    ) -> Tuple[int, int]:
        """
        并行处理大文件

        Args:
            file_content: 文件内容
            batch_id: 批次ID
            metric_type_id: 指标类型ID
            metric_code: 指标代码
            data_date: 数据日期
            num_workers: 并行工作线程数
        """

        # 1. 分割文件为多个块
        chunks = self._split_file_into_chunks(file_content, num_workers)

        logger.info(f"文件分割为{len(chunks)}个块进行并行处理")

        # 2. 创建线程池并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []

            for chunk_id, chunk in enumerate(chunks):
                future = executor.submit(
                    self._process_chunk,
                    chunk,
                    chunk_id,
                    batch_id,
                    metric_type_id,
                    metric_code,
                    data_date
                )
                futures.append(future)

            # 3. 收集结果
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"块{result.chunk_id}处理完成: 成功{result.success_count}条")
                except Exception as e:
                    logger.error(f"块处理失败: {e}")

        # 4. 合并结果并计算
        return self._merge_and_compute(results, batch_id, metric_type_id, metric_code, data_date)

    def _split_file_into_chunks(self, file_content: bytes, num_chunks: int) -> List[bytes]:
        """
        智能分割文件，确保每个块在行边界处分割
        """
        try:
            content = file_content.decode('utf-8')
        except:
            content = file_content.decode('gbk')

        lines = content.strip().split('\n')
        total_lines = len(lines)

        # 计算每个块的大小
        chunk_size = max(1, total_lines // num_chunks)

        chunks = []
        for i in range(num_chunks):
            start_idx = i * chunk_size
            if i == num_chunks - 1:
                # 最后一个块包含所有剩余行
                end_idx = total_lines
            else:
                end_idx = (i + 1) * chunk_size

            chunk_lines = lines[start_idx:end_idx]
            if chunk_lines:
                chunk_content = '\n'.join(chunk_lines).encode('utf-8')
                chunks.append(chunk_content)

        return chunks

    def _process_chunk(
        self,
        chunk_content: bytes,
        chunk_id: int,
        batch_id: int,
        metric_type_id: int,
        metric_code: str,
        data_date
    ) -> ChunkResult:
        """
        处理单个块
        """
        # 为每个线程创建独立的session
        session = self.db_session_factory()

        try:
            # 导入优化的TXT服务
            from app.services.optimized_txt_import import OptimizedTXTImportService, TradeData

            service = OptimizedTXTImportService(session)

            # 解析块内容
            trade_data_list = service._parse_file_content(chunk_content, data_date)

            # 预加载映射（每个线程独立加载）
            service.preload_mappings()

            # 过滤有效数据
            valid_trades = [
                td for td in trade_data_list
                if td.stock_code in service.valid_stocks
            ]

            # 返回结果（不立即写入数据库）
            return ChunkResult(
                chunk_id=chunk_id,
                success_count=len(valid_trades),
                error_count=len(trade_data_list) - len(valid_trades),
                data=valid_trades
            )

        except Exception as e:
            logger.error(f"块{chunk_id}处理失败: {e}")
            return ChunkResult(chunk_id=chunk_id, success_count=0, error_count=0, data=[])

        finally:
            session.close()

    def _merge_and_compute(
        self,
        results: List[ChunkResult],
        batch_id: int,
        metric_type_id: int,
        metric_code: str,
        data_date
    ) -> Tuple[int, int]:
        """
        合并所有块的结果并进行最终计算
        """
        # 创建主session
        session = self.db_session_factory()

        try:
            from app.services.optimized_txt_import import OptimizedTXTImportService

            service = OptimizedTXTImportService(session)
            service.preload_mappings()

            # 合并所有交易数据
            all_trades = []
            total_success = 0
            total_error = 0

            for result in results:
                all_trades.extend(result.data)
                total_success += result.success_count
                total_error += result.error_count

            logger.info(f"合并完成: 总计{len(all_trades)}条有效数据")

            # 批量导入原始数据
            service._bulk_import_raw_data(all_trades, batch_id, metric_type_id, metric_code)

            # 计算排名和汇总
            service._compute_rankings_in_memory(
                all_trades,
                batch_id,
                metric_type_id,
                metric_code,
                data_date
            )

            session.commit()

            return total_success, total_error

        except Exception as e:
            session.rollback()
            logger.error(f"合并和计算失败: {e}")
            raise

        finally:
            session.close()


class AsyncImportQueue:
    """
    异步导入队列管理器
    用于管理多个文件的并发导入
    """

    def __init__(self, max_concurrent_imports: int = 3):
        self.max_concurrent = max_concurrent_imports
        self.import_queue = Queue()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent)
        self.active_imports = {}
        self.lock = threading.Lock()

    def add_import_task(self, task_info: dict):
        """添加导入任务到队列"""
        self.import_queue.put(task_info)

        # 尝试启动新的导入任务
        self._start_next_import()

    def _start_next_import(self):
        """启动下一个导入任务"""
        with self.lock:
            if len(self.active_imports) >= self.max_concurrent:
                return

            if self.import_queue.empty():
                return

            task_info = self.import_queue.get()
            batch_id = task_info['batch_id']

            # 提交任务到线程池
            future = self.executor.submit(self._execute_import, task_info)
            self.active_imports[batch_id] = future

            # 设置完成回调
            future.add_done_callback(lambda f: self._on_import_complete(batch_id))

    def _execute_import(self, task_info: dict):
        """执行导入任务"""
        try:
            # 根据文件类型选择处理器
            if task_info['file_type'] == 'TXT':
                return self._process_txt_import(task_info)
            else:
                return self._process_csv_import(task_info)
        except Exception as e:
            logger.error(f"导入任务失败: {e}")
            raise

    def _process_txt_import(self, task_info: dict):
        """处理TXT导入"""
        # 创建session factory
        engine = create_engine(settings.DATABASE_URL)
        SessionFactory = sessionmaker(bind=engine)

        # 使用并行导入服务
        service = ParallelTXTImportService(SessionFactory)

        return service.process_large_file(
            task_info['file_content'],
            task_info['batch_id'],
            task_info['metric_type_id'],
            task_info['metric_code'],
            task_info['data_date'],
            num_workers=4
        )

    def _process_csv_import(self, task_info: dict):
        """处理CSV导入"""
        # 实现CSV导入逻辑
        pass

    def _on_import_complete(self, batch_id: int):
        """导入完成回调"""
        with self.lock:
            if batch_id in self.active_imports:
                del self.active_imports[batch_id]
                logger.info(f"批次{batch_id}导入完成")

            # 启动下一个任务
            self._start_next_import()

    def get_status(self) -> dict:
        """获取队列状态"""
        with self.lock:
            return {
                'queued': self.import_queue.qsize(),
                'active': len(self.active_imports),
                'active_batches': list(self.active_imports.keys())
            }

    def shutdown(self):
        """关闭队列"""
        self.executor.shutdown(wait=True)