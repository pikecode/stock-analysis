#!/usr/bin/env python3
"""
数据库结构对比工具
比较本地数据库和生产数据库的表结构差异
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from tabulate import tabulate
from typing import Dict, List, Tuple, Set


def get_db_connection(env: str):
    """获取数据库连接"""
    if env == "local":
        return psycopg2.connect(
            host="localhost",
            port=5432,
            database="stock_analysis",
            user="peak"
        )
    elif env == "production":
        return psycopg2.connect(
            host="82.157.28.35",
            port=5432,
            database="stock_analysis",
            user="stock_user",
            password="stock_pass_2024"
        )
    else:
        raise ValueError(f"Unknown environment: {env}")


def get_table_columns(conn, table_name: str) -> Dict[str, Dict]:
    """获取表的所有列信息"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))

    columns = {}
    for row in cursor.fetchall():
        col_name = row[0]
        columns[col_name] = {
            'type': row[1],
            'max_length': row[2],
            'precision': row[3],
            'scale': row[4],
            'nullable': row[5],
            'default': row[6]
        }

    cursor.close()
    return columns


def get_all_tables(conn) -> Set[str]:
    """获取所有表名"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return tables


def format_column_type(col_info: Dict) -> str:
    """格式化列类型"""
    type_str = col_info['type']

    if col_info['max_length']:
        type_str += f"({col_info['max_length']})"
    elif col_info['precision']:
        if col_info['scale']:
            type_str += f"({col_info['precision']},{col_info['scale']})"
        else:
            type_str += f"({col_info['precision']})"

    if col_info['nullable'] == 'NO':
        type_str += " NOT NULL"

    if col_info['default']:
        default = col_info['default'][:50]  # 截断过长的默认值
        type_str += f" DEFAULT {default}"

    return type_str


def compare_tables(local_conn, prod_conn, table_name: str):
    """比较单个表的结构"""
    print(f"\n{'='*80}")
    print(f"表: {table_name}")
    print('='*80)

    local_cols = get_table_columns(local_conn, table_name)
    prod_cols = get_table_columns(prod_conn, table_name)

    local_col_names = set(local_cols.keys())
    prod_col_names = set(prod_cols.keys())

    # 只在本地存在的列
    local_only = local_col_names - prod_col_names
    if local_only:
        print("\n❌ 生产环境缺少的列:")
        for col in sorted(local_only):
            print(f"  - {col}: {format_column_type(local_cols[col])}")

    # 只在生产存在的列
    prod_only = prod_col_names - local_col_names
    if prod_only:
        print("\n⚠️  本地环境缺少的列（生产环境多余）:")
        for col in sorted(prod_only):
            print(f"  - {col}: {format_column_type(prod_cols[col])}")

    # 共同列的差异
    common_cols = local_col_names & prod_col_names
    differences = []

    for col in sorted(common_cols):
        local_type = format_column_type(local_cols[col])
        prod_type = format_column_type(prod_cols[col])

        if local_type != prod_type:
            differences.append([
                col,
                prod_type,
                local_type
            ])

    if differences:
        print("\n⚠️  列定义不一致:")
        print(tabulate(differences,
                      headers=['列名', '生产环境', '本地环境'],
                      tablefmt='grid'))

    if not local_only and not prod_only and not differences:
        print("\n✅ 表结构完全一致")


def main():
    """主函数"""
    print("="*80)
    print("数据库结构对比工具")
    print("="*80)
    print("本地: localhost:5432/stock_analysis (user: peak)")
    print("生产: 82.157.28.35:5432/stock_analysis (user: stock_user)")
    print("="*80)

    try:
        # 连接数据库
        print("\n正在连接数据库...")
        local_conn = get_db_connection("local")
        prod_conn = get_db_connection("production")
        print("✅ 数据库连接成功\n")

        # 获取所有表
        local_tables = get_all_tables(local_conn)
        prod_tables = get_all_tables(prod_conn)

        # 表差异
        local_only_tables = local_tables - prod_tables
        prod_only_tables = prod_tables - local_tables
        common_tables = local_tables & prod_tables

        if local_only_tables:
            print("\n❌ 生产环境缺少的表:")
            for table in sorted(local_only_tables):
                print(f"  - {table}")

        if prod_only_tables:
            print("\n⚠️  本地环境缺少的表（生产环境多余）:")
            for table in sorted(prod_only_tables):
                print(f"  - {table}")

        # 比较共同表
        print(f"\n正在比较 {len(common_tables)} 个共同表...")

        # 重点关注的表
        important_tables = [
            'users', 'plans', 'subscriptions', 'subscription_logs',
            'stocks', 'concepts', 'stock_concepts'
        ]

        # 先比较重要表
        for table in important_tables:
            if table in common_tables:
                compare_tables(local_conn, prod_conn, table)

        # 询问是否比较所有表
        print(f"\n还有 {len(common_tables) - len([t for t in important_tables if t in common_tables])} 个其他表")
        response = input("是否比较所有表? (y/N): ").strip().lower()

        if response == 'y':
            for table in sorted(common_tables):
                if table not in important_tables:
                    compare_tables(local_conn, prod_conn, table)

        # 关闭连接
        local_conn.close()
        prod_conn.close()

        print("\n" + "="*80)
        print("对比完成！")
        print("="*80)

    except psycopg2.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
