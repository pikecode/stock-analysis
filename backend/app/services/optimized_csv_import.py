"""优化的CSV导入服务 - 股票概念映射"""
from typing import Dict, Set, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from io import BytesIO, StringIO
import csv


class OptimizedCSVImportService:
    """优化的CSV导入服务：高效处理股票-概念映射关系和行业映射"""

    def __init__(self, db: Session):
        self.db = db
        self.concept_cache: Dict[str, int] = {}  # 概念名称到ID的缓存
        self.stock_cache: Set[str] = set()  # 已存在的股票代码缓存
        self.industry_cache: Dict[str, int] = {}  # 行业名称到ID的缓存

    def preload_cache(self):
        """预加载缓存数据，减少查询"""
        # 预加载所有概念
        concepts = self.db.execute(
            text("SELECT id, concept_name FROM concepts")
        ).fetchall()
        self.concept_cache = {c.concept_name: c.id for c in concepts}

        # 预加载所有股票代码
        stocks = self.db.execute(
            text("SELECT stock_code FROM stocks")
        ).fetchall()
        self.stock_cache = {s.stock_code for s in stocks}

        # 预加载所有行业
        industries = self.db.execute(
            text("SELECT id, industry_name FROM industries")
        ).fetchall()
        self.industry_cache = {ind.industry_name: ind.id for ind in industries}

    def parse_and_import_optimized(
        self,
        batch_id: int,
        file_content: bytes
    ) -> Tuple[int, int]:
        """优化版CSV导入"""

        # 1. 预加载缓存
        self.preload_cache()

        # 2. 使用pandas高效读取
        df = pd.read_csv(BytesIO(file_content), encoding="utf-8", dtype=str)

        # 3. 批量收集数据
        new_stocks = []
        new_concepts = []
        stock_concept_mappings = []
        new_industries = []
        stock_industry_mappings = []
        raw_mappings = []

        # 检测列名
        stock_code_col = self._find_column(
            df.columns.tolist(),
            ["股票代码", "code", "stock_code", "代码"]
        )
        stock_name_col = self._find_column(
            df.columns.tolist(),
            ["股票名称", "name", "stock_name", "名称"]
        )
        concept_col = self._find_column(
            df.columns.tolist(),
            ["概念", "concept", "板块", "concept_name"]
        )
        industry_col = self._find_column(
            df.columns.tolist(),
            ["行业", "industry", "industry_name"]
        )

        # 4. 处理数据
        for row_idx, (_, row) in enumerate(df.iterrows(), 1):
            stock_code = str(row[stock_code_col]).strip()
            if not stock_code or stock_code == "nan":
                continue

            stock_name = str(row[stock_name_col]).strip() if stock_name_col else None
            concept_name = str(row[concept_col]).strip() if concept_col else None
            industry_name = str(row[industry_col]).strip() if industry_col else None

            # 清理行业名称（处理None、nan等）
            if not industry_name or industry_name == "None" or industry_name == "nan":
                industry_name = None

            # 收集新股票
            if stock_code not in self.stock_cache:
                new_stocks.append({
                    'code': stock_code,
                    'name': stock_name
                })
                self.stock_cache.add(stock_code)

            # 收集新概念
            if concept_name and concept_name not in self.concept_cache:
                new_concepts.append(concept_name)

            # 收集新行业
            if industry_name and industry_name not in self.industry_cache:
                new_industries.append(industry_name)

            # 收集映射关系
            if concept_name:
                stock_concept_mappings.append({
                    'stock_code': stock_code,
                    'concept_name': concept_name
                })

            # 收集行业映射
            if industry_name:
                stock_industry_mappings.append({
                    'stock_code': stock_code,
                    'industry_name': industry_name
                })

            # 收集原始数据（审计用）
            raw_mappings.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'concept_name': concept_name,
                'industry_name': industry_name,
                'source_row_number': row_idx
            })

        # 5. 批量插入
        success_count = self._batch_insert_all(
            new_stocks,
            new_concepts,
            stock_concept_mappings,
            new_industries,
            stock_industry_mappings,
            raw_mappings,
            batch_id
        )

        return success_count, 0

    def _batch_insert_all(
        self,
        new_stocks: List[Dict],
        new_concepts: List[str],
        mappings: List[Dict],
        new_industries: List[str],
        stock_industry_mappings: List[Dict],
        raw_mappings: List[Dict],
        batch_id: int
    ) -> int:
        """批量插入所有数据"""

        # 1. 批量插入新股票（使用COPY）
        if new_stocks:
            self._bulk_copy_stocks(new_stocks)

        # 2. 批量插入新概念
        if new_concepts:
            self._bulk_insert_concepts(new_concepts)
            # 更新概念缓存
            self._refresh_concept_cache(new_concepts)

        # 3. 批量插入新行业（新增）
        if new_industries:
            self._bulk_insert_industries(new_industries)
            # 更新行业缓存
            self._refresh_industry_cache(new_industries)

        # 4. 批量更新股票-概念映射（先删除再插入，确保数据最新）
        if mappings:
            self._bulk_update_mappings(mappings)

        # 5. 批量插入股票-行业映射（新增）
        if stock_industry_mappings:
            self._bulk_insert_industry_mappings(stock_industry_mappings)

        # 6. 批量插入原始数据（可选审计）
        if raw_mappings:
            self._bulk_insert_raw_mappings(raw_mappings, batch_id)

        # 7. 记录导入历史
        self._record_import_history(batch_id, mappings)

        self.db.commit()
        return len(mappings)

    def _bulk_copy_stocks(self, stocks: List[Dict]):
        """批量插入股票（使用INSERT...ON CONFLICT）"""
        if not stocks:
            return

        # 使用INSERT...ON CONFLICT（COPY不支持冲突处理）
        values = []
        for stock in stocks:
            code = stock['code'].replace("'", "''")
            name = stock['name'].replace("'", "''") if stock['name'] else None
            if name:
                values.append(f"('{code}', '{name}')")
            else:
                values.append(f"('{code}', NULL)")

        # 分批插入避免SQL过长
        batch_size = 1000
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            sql = text(f"""
                INSERT INTO stocks (stock_code, stock_name)
                VALUES {','.join(batch)}
                ON CONFLICT (stock_code) DO UPDATE
                SET stock_name = COALESCE(EXCLUDED.stock_name, stocks.stock_name)
            """)
            self.db.execute(sql)

    def _bulk_insert_concepts(self, concepts: List[str]):
        """批量插入概念"""
        if not concepts:
            return

        # 使用VALUES子句批量插入
        values = ", ".join([f"('{c}')" for c in concepts])
        sql = text(f"""
            INSERT INTO concepts (concept_name)
            VALUES {values}
            ON CONFLICT (concept_name) DO NOTHING
        """)
        self.db.execute(sql)

    def _bulk_update_mappings(self, mappings: List[Dict]):
        """批量更新股票-概念映射关系"""

        # 1. 收集所有涉及的股票
        stock_codes = list(set(m['stock_code'] for m in mappings))

        # 2. 删除这些股票的旧映射（全量更新策略）
        if stock_codes:
            placeholders = ','.join([f"'{code}'" for code in stock_codes])
            self.db.execute(text(f"""
                DELETE FROM stock_concepts
                WHERE stock_code IN ({placeholders})
            """))

        # 3. 批量插入新映射关系
        values_list = []
        for mapping in mappings:
            concept_id = self.concept_cache.get(mapping['concept_name'])
            if concept_id:
                values_list.append(
                    f"('{mapping['stock_code']}', {concept_id})"
                )

        if values_list:
            # 分批插入避免SQL过长
            batch_size = 5000
            for i in range(0, len(values_list), batch_size):
                batch = values_list[i:i + batch_size]
                sql = text(f"""
                    INSERT INTO stock_concepts (stock_code, concept_id)
                    VALUES {','.join(batch)}
                    ON CONFLICT (stock_code, concept_id) DO NOTHING
                """)
                self.db.execute(sql)

    def _refresh_concept_cache(self, new_concepts: List[str]):
        """刷新概念缓存"""
        if not new_concepts:
            return

        placeholders = ','.join([f"'{c}'" for c in new_concepts])
        result = self.db.execute(text(f"""
            SELECT id, concept_name FROM concepts
            WHERE concept_name IN ({placeholders})
        """)).fetchall()

        for r in result:
            self.concept_cache[r.concept_name] = r.id

    def _bulk_insert_industries(self, industries: List[str]):
        """批量插入行业"""
        if not industries:
            return

        # 使用VALUES子句批量插入
        unique_industries = list(set(industries))  # 去重
        values = []
        for ind in unique_industries:
            escaped_ind = ind.replace("'", "''")
            values.append(f"('{escaped_ind}', 1)")

        values_str = ", ".join(values)
        sql = text(f"""
            INSERT INTO industries (industry_name, level)
            VALUES {values_str}
            ON CONFLICT (industry_name) DO NOTHING
        """)
        self.db.execute(sql)

    def _refresh_industry_cache(self, new_industries: List[str]):
        """刷新行业缓存"""
        if not new_industries:
            return

        unique_industries = list(set(new_industries))
        placeholders = []
        for ind in unique_industries:
            escaped_ind = ind.replace("'", "''")
            placeholders.append(f"'{escaped_ind}'")

        placeholders_str = ','.join(placeholders)
        result = self.db.execute(text(f"""
            SELECT id, industry_name FROM industries
            WHERE industry_name IN ({placeholders_str})
        """)).fetchall()

        for r in result:
            self.industry_cache[r.industry_name] = r.id

    def _bulk_insert_industry_mappings(self, mappings: List[Dict]):
        """批量插入股票-行业映射"""
        if not mappings:
            return

        # 分批插入避免SQL过长
        batch_size = 5000
        values_list = []

        for mapping in mappings:
            industry_id = self.industry_cache.get(mapping['industry_name'])
            if industry_id:
                values_list.append(
                    f"('{mapping['stock_code']}', {industry_id})"
                )

        if values_list:
            for i in range(0, len(values_list), batch_size):
                batch = values_list[i:i + batch_size]
                sql = text(f"""
                    INSERT INTO stock_industries (stock_code, industry_id)
                    VALUES {','.join(batch)}
                    ON CONFLICT (stock_code, industry_id) DO NOTHING
                """)
                self.db.execute(sql)

    def _bulk_insert_raw_mappings(self, mappings: List[Dict], batch_id: int):
        """批量插入原始映射数据（审计用）"""
        if not mappings:
            return

        # 分批插入避免SQL过长
        batch_size = 1000

        for batch_idx in range(0, len(mappings), batch_size):
            batch_records = mappings[batch_idx:batch_idx + batch_size]
            values = []

            for m in batch_records:
                stock_code = m['stock_code'].replace("'", "''")
                stock_name_val = m['stock_name'].replace("'", "''") if m['stock_name'] else None
                concept_name_val = m['concept_name'].replace("'", "''") if m['concept_name'] else None
                industry_name_val = m['industry_name'].replace("'", "''") if m['industry_name'] else None

                stock_name = f"'{stock_name_val}'" if stock_name_val else "NULL"
                concept_name = f"'{concept_name_val}'" if concept_name_val else "NULL"
                industry_name = f"'{industry_name_val}'" if industry_name_val else "NULL"

                values.append(f"""(
                    {batch_id},
                    '{stock_code}',
                    {stock_name},
                    {concept_name},
                    {industry_name},
                    NULL,
                    {m['source_row_number']},
                    true,
                    NULL
                )""")

            insert_sql = f"""
                INSERT INTO stock_concept_mapping_raw (
                    import_batch_id, stock_code, stock_name, concept_name,
                    industry_name, extra_fields, source_row_number, is_valid,
                    validation_errors
                )
                VALUES {','.join(values)}
                ON CONFLICT DO NOTHING
            """
            self.db.execute(text(insert_sql))

    def _record_import_history(self, batch_id: int, mappings: List[Dict]):
        """记录导入历史用于审计"""
        # 可以记录本次导入更新了哪些映射关系
        sql = text("""
            UPDATE import_batches
            SET success_rows = :count,
                total_rows = :count,
                status = 'completed',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = :batch_id
        """)
        self.db.execute(sql, {
            'batch_id': batch_id,
            'count': len(mappings)
        })

    def _find_column(self, columns: list, candidates: list) -> str:
        """查找匹配的列名"""
        for col in columns:
            col_lower = col.lower().strip()
            for candidate in candidates:
                if candidate.lower() in col_lower:
                    return col
        return None