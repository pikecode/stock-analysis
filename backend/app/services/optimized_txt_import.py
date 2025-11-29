"""优化的TXT导入服务 - 股票交易数据导入与计算"""
from typing import Dict, Set, List, Tuple, Optional
from datetime import date, datetime
from dataclasses import dataclass
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text
import concurrent.futures
from io import StringIO
import csv
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradeData:
    """交易数据结构"""
    stock_code: str
    trade_date: date
    trade_value: int
    exchange_prefix: Optional[str] = None


class OptimizedTXTImportService:
    """优化的TXT导入服务：高效处理交易数据并计算排名"""

    def __init__(self, db: Session):
        self.db = db
        # 预加载缓存
        self.stock_concepts_map: Dict[str, List[int]] = {}  # 股票到概念ID列表的映射
        self.valid_stocks: Set[str] = set()  # 有概念关联的股票集合
        self.concept_stocks_map: Dict[int, Set[str]] = defaultdict(set)  # 概念到股票集合的映射

    def preload_mappings(self):
        """预加载股票-概念映射关系，避免重复查询"""
        # 加载所有股票-概念映射
        mappings = self.db.execute(text("""
            SELECT sc.stock_code, sc.concept_id, c.concept_name
            FROM stock_concepts sc
            JOIN concepts c ON c.id = sc.concept_id
        """)).fetchall()

        for mapping in mappings:
            stock_code = mapping.stock_code
            concept_id = mapping.concept_id

            # 股票到概念映射
            if stock_code not in self.stock_concepts_map:
                self.stock_concepts_map[stock_code] = []
            self.stock_concepts_map[stock_code].append(concept_id)

            # 概念到股票映射
            self.concept_stocks_map[concept_id].add(stock_code)

            # 有效股票集合
            self.valid_stocks.add(stock_code)

        logger.info(f"预加载完成: {len(self.valid_stocks)}个有效股票, {len(self.concept_stocks_map)}个概念")

    def parse_and_import_with_compute(
        self,
        batch_id: int,
        file_content: bytes,
        metric_type_id: int,
        metric_code: str,
        data_date: date
    ) -> Tuple[int, int]:
        """解析TXT文件，导入数据并立即进行计算"""

        # 1. 预加载映射关系
        self.preload_mappings()

        # 2. 解析文件内容
        trade_data_list = self._parse_file_content(file_content, data_date)

        # 3. 过滤有效数据（只保留有概念关联的股票）
        valid_trades = [
            td for td in trade_data_list
            if td.stock_code in self.valid_stocks
        ]

        invalid_count = len(trade_data_list) - len(valid_trades)

        logger.info(f"解析完成: 总计{len(trade_data_list)}条, 有效{len(valid_trades)}条")

        # 4. 批量导入原始数据
        self._bulk_import_raw_data(valid_trades, batch_id, metric_type_id, metric_code)

        # 5. 直接在内存中计算排名和汇总
        self._compute_rankings_in_memory(
            valid_trades,
            batch_id,
            metric_type_id,
            metric_code,
            data_date
        )

        # 6. 提交事务
        self.db.commit()

        return len(valid_trades), invalid_count

    def _parse_file_content(self, file_content: bytes, default_date: date) -> List[TradeData]:
        """解析文件内容为交易数据列表"""
        # 尝试不同编码
        try:
            content = file_content.decode('utf-8')
        except:
            content = file_content.decode('gbk')

        trade_data_list = []
        lines = content.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # 解析行数据（制表符或空格分隔）
            parts = line.split('\t') if '\t' in line else line.split()
            if len(parts) < 3:
                continue

            # 解析字段
            stock_code_raw = parts[0].strip()
            trade_date_str = parts[1].strip()
            trade_value_str = parts[2].strip()

            # 处理股票代码前缀
            stock_code, exchange_prefix = self._parse_stock_code(stock_code_raw)

            # 处理日期
            trade_date = self._parse_date(trade_date_str, default_date)

            # 处理交易值
            try:
                trade_value = int(float(trade_value_str))
            except:
                continue

            trade_data_list.append(TradeData(
                stock_code=stock_code,
                trade_date=trade_date,
                trade_value=trade_value,
                exchange_prefix=exchange_prefix
            ))

        return trade_data_list

    def _parse_stock_code(self, raw_code: str) -> Tuple[str, Optional[str]]:
        """解析股票代码，分离前缀"""
        raw_code = raw_code.upper().strip()

        # 处理交易所前缀
        if raw_code.startswith(('SH', 'SZ', 'BJ')):
            return raw_code[2:], raw_code[:2]

        return raw_code, None

    def _parse_date(self, date_str: str, default_date: date) -> date:
        """解析日期字符串"""
        if not date_str or date_str == 'nan':
            return default_date

        # 尝试多种日期格式
        for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue

        return default_date

    def _bulk_import_raw_data(
        self,
        trade_data_list: List[TradeData],
        batch_id: int,
        metric_type_id: int,
        metric_code: str
    ):
        """使用COPY命令批量导入原始数据"""
        if not trade_data_list:
            return

        # 获取数据日期（从第一条数据）
        trade_date = trade_data_list[0].trade_date

        # 获取原生连接和游标
        conn = self.db.connection().connection
        cursor = conn.cursor()

        # 第1步：删除该日期该指标的旧原始数据
        cursor.execute("""
            DELETE FROM stock_metric_data_raw
            WHERE metric_type_id = %s AND trade_date = %s
        """, (metric_type_id, trade_date))

        delete_count = cursor.rowcount
        logger.info(f"删除旧原始数据: {delete_count}条")

        # 关键：提交删除操作，确保后续COPY能看到最新状态
        conn.commit()

        # 第2步：准备COPY数据
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')

        for idx, td in enumerate(trade_data_list, 1):
            writer.writerow([
                batch_id,
                metric_type_id,
                metric_code,
                f"{td.exchange_prefix or ''}{td.stock_code}",  # 原始代码
                td.stock_code,  # 净代码
                td.exchange_prefix or '',
                td.trade_date.isoformat(),
                td.trade_value,
                idx,  # 源行号
                True  # is_valid
            ])

        output.seek(0)

        # 第3步：使用COPY命令高速导入
        cursor.copy_expert(
            """
            COPY stock_metric_data_raw (
                import_batch_id, metric_type_id, metric_code,
                stock_code_raw, stock_code, exchange_prefix,
                trade_date, trade_value, source_row_number, is_valid
            )
            FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '')
            """,
            output
        )

        logger.info(f"导入原始数据: {len(trade_data_list)}条完成")

    def _compute_rankings_in_memory(
        self,
        trade_data_list: List[TradeData],
        batch_id: int,
        metric_type_id: int,
        metric_code: str,
        data_date: date
    ):
        """在内存中计算排名和汇总，然后批量写入"""

        # 1. 按概念分组数据
        concept_trades: Dict[int, List[TradeData]] = defaultdict(list)

        for td in trade_data_list:
            # 获取股票所属概念
            concept_ids = self.stock_concepts_map.get(td.stock_code, [])
            for concept_id in concept_ids:
                concept_trades[concept_id].append(td)

        # 2. 计算每个概念的排名和统计
        rankings = []
        summaries = []

        for concept_id, trades in concept_trades.items():
            if not trades:
                continue

            # 排序计算排名
            sorted_trades = sorted(trades, key=lambda x: x.trade_value, reverse=True)
            total_stocks = len(sorted_trades)

            # 计算统计值
            values = [t.trade_value for t in sorted_trades]
            total_value = sum(values)
            avg_value = total_value // total_stocks if total_stocks > 0 else 0
            max_value = values[0] if values else 0
            min_value = values[-1] if values else 0

            # 中位数
            median_value = self._calculate_median(values)

            # 生成排名记录
            for rank, td in enumerate(sorted_trades, 1):
                rankings.append({
                    'metric_type_id': metric_type_id,
                    'metric_code': metric_code,
                    'concept_id': concept_id,
                    'stock_code': td.stock_code,
                    'trade_date': data_date,
                    'trade_value': td.trade_value,
                    'rank': rank,
                    'import_batch_id': batch_id
                })

            # 生成汇总记录
            summaries.append({
                'metric_type_id': metric_type_id,
                'metric_code': metric_code,
                'concept_id': concept_id,
                'trade_date': data_date,
                'total_value': total_value,
                'avg_value': avg_value,
                'max_value': max_value,
                'min_value': min_value,
                'median_value': median_value,
                'import_batch_id': batch_id
            })

        # 3. 批量插入排名数据
        self._bulk_insert_rankings(rankings)

        # 4. 批量插入汇总数据
        self._bulk_insert_summaries(summaries)

        logger.info(f"计算完成: {len(rankings)}条排名, {len(summaries)}条汇总")

    def _calculate_median(self, values: List[int]) -> int:
        """计算中位数"""
        if not values:
            return 0

        sorted_values = sorted(values)
        n = len(sorted_values)

        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) // 2
        else:
            return sorted_values[n//2]

    def _bulk_insert_rankings(self, rankings: List[Dict]):
        """批量插入排名数据"""
        if not rankings:
            return

        metric_type_id = rankings[0]['metric_type_id']
        trade_date = rankings[0]['trade_date']

        # 获取原生连接和游标
        conn = self.db.connection().connection
        cursor = conn.cursor()

        # 第1步：删除旧数据
        cursor.execute("""
            DELETE FROM concept_stock_daily_rank
            WHERE metric_type_id = %s AND trade_date = %s
        """, (metric_type_id, trade_date))

        delete_count = cursor.rowcount
        logger.info(f"删除旧排名数据: {delete_count}条")

        # 关键：提交删除操作，确保后续COPY能看到最新状态
        conn.commit()

        # 第2步：准备COPY数据
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')

        for r in rankings:
            writer.writerow([
                r['metric_type_id'],
                r['metric_code'],
                r['concept_id'],
                r['stock_code'],
                r['trade_date'].isoformat(),
                r['trade_value'],
                r['rank'],
                r['import_batch_id']
            ])

        output.seek(0)

        # 第3步：使用 INSERT...ON CONFLICT 插入新数据（处理重复）
        if rankings:
            # 分批插入避免SQL过长
            batch_size = 1000
            for batch_idx in range(0, len(rankings), batch_size):
                batch_records = rankings[batch_idx:batch_idx + batch_size]
                values = []

                for r in batch_records:
                    # 正确处理字符串转义
                    values.append(f"""(
                        {r['metric_type_id']},
                        '{r['metric_code'].replace("'", "''")}',
                        {r['concept_id']},
                        '{r['stock_code'].replace("'", "''")}',
                        '{r['trade_date']}',
                        {r['trade_value']},
                        {r['rank']},
                        {r['import_batch_id']}
                    )""")

                insert_sql = f"""
                    INSERT INTO concept_stock_daily_rank (
                        metric_type_id, metric_code, concept_id, stock_code,
                        trade_date, trade_value, rank, import_batch_id
                    )
                    VALUES {','.join(values)}
                    ON CONFLICT (metric_type_id, concept_id, stock_code, trade_date)
                    DO NOTHING
                """
                cursor.execute(insert_sql)

        logger.info(f"插入排名数据: {len(rankings)}条（重复自动跳过）")

    def _bulk_insert_summaries(self, summaries: List[Dict]):
        """批量插入汇总数据"""
        if not summaries:
            return

        metric_type_id = summaries[0]['metric_type_id']
        trade_date = summaries[0]['trade_date']

        # 获取原生连接和游标
        conn = self.db.connection().connection
        cursor = conn.cursor()

        # 第1步：删除旧数据
        cursor.execute("""
            DELETE FROM concept_daily_summary
            WHERE metric_type_id = %s AND trade_date = %s
        """, (metric_type_id, trade_date))

        delete_count = cursor.rowcount
        logger.info(f"删除旧汇总数据: {delete_count}条")

        # 关键：提交删除操作，确保后续COPY能看到最新状态
        conn.commit()

        # 第2步：准备COPY数据
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')

        for s in summaries:
            writer.writerow([
                s['metric_type_id'],
                s['metric_code'],
                s['concept_id'],
                s['trade_date'].isoformat(),
                s['total_value'],
                s['avg_value'],
                s['max_value'],
                s['min_value'],
                s['median_value'],
                s['top10_sum'],
                s['import_batch_id']
            ])

        output.seek(0)

        # 第3步：使用 INSERT...ON CONFLICT 插入新数据（处理重复）
        if summaries:
            # 分批插入避免SQL过长
            batch_size = 1000
            for batch_idx in range(0, len(summaries), batch_size):
                batch_records = summaries[batch_idx:batch_idx + batch_size]
                values = []

                for s in batch_records:
                    # 正确处理字符串转义
                    values.append(f"""(
                        {s['metric_type_id']},
                        '{s['metric_code'].replace("'", "''")}',
                        {s['concept_id']},
                        '{s['trade_date']}',
                        {s['total_value']},
                        {s['avg_value']},
                        {s['max_value']},
                        {s['min_value']},
                        {s['median_value']},
                        {s['top10_sum']},
                        {s['import_batch_id']}
                    )""")

                insert_sql = f"""
                    INSERT INTO concept_daily_summary (
                        metric_type_id, metric_code, concept_id, trade_date,
                        total_value, avg_value, max_value, min_value,
                        median_value, top10_sum, import_batch_id
                    )
                    VALUES {','.join(values)}
                    ON CONFLICT (metric_type_id, concept_id, trade_date)
                    DO NOTHING
                """
                cursor.execute(insert_sql)

        logger.info(f"插入汇总数据: {len(summaries)}条（重复自动跳过）")