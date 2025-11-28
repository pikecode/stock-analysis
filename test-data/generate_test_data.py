#!/usr/bin/env python3
"""
测试数据生成脚本
生成用于导入功能测试的 CSV 和 TXT 文件
"""

import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============ 配置 ============

STOCKS = [
    # 上海（SH）股票
    ("600000", "浦发银行", "SH"),
    ("600004", "白云机场", "SH"),
    ("600006", "东方集团", "SH"),
    ("600007", "巨龙集团", "SH"),
    ("600008", "首创集团", "SH"),
    ("600009", "上海机场", "SH"),
    ("600010", "包钢股份", "SH"),
    ("600011", "华能国际", "SH"),
    ("600012", "皖通高速", "SH"),
    ("600015", "华夏银行", "SH"),
    ("600016", "民生银行", "SH"),
    ("600017", "新华保险", "SH"),
    ("600018", "上港集团", "SH"),
    ("600019", "宝钢股份", "SH"),
    ("600020", "中原高速", "SH"),
    ("600021", "上海电力", "SH"),
    ("600022", "山东钢铁", "SH"),
    ("600023", "浙能电力", "SH"),
    ("600025", "华能水电", "SH"),
    ("600026", "中远海能", "SH"),
    # 深圳（SZ）股票
    ("000001", "平安银行", "SZ"),
    ("000002", "万科A", "SZ"),
    ("000004", "国农科技", "SZ"),
    ("000005", "世纪星源", "SZ"),
    ("000006", "深振业A", "SZ"),
    ("000007", "全新好", "SZ"),
    ("000008", "神州高铁", "SZ"),
    ("000009", "中国宝安", "SZ"),
    ("000010", "美丽生态", "SZ"),
    ("000011", "深物业A", "SZ"),
    ("000012", "南玻A", "SZ"),
    ("000013", "一致药业", "SZ"),
    ("000014", "宝安地产", "SZ"),
    ("000015", "深康佳A", "SZ"),
    ("000016", "深中华A", "SZ"),
    ("000017", "深中华B", "SZ"),
    ("000018", "泛海控股", "SZ"),
    ("000019", "深深房A", "SZ"),
    ("000020", "深深房B", "SZ"),
    ("000021", "深科技", "SZ"),
    ("000022", "深赤湾A", "SZ"),
    ("000023", "深赤湾B", "SZ"),
    ("000024", "深高速", "SZ"),
    ("000025", "特力A", "SZ"),
    ("000026", "飞亚达A", "SZ"),
    ("000027", "深圳能源", "SZ"),
    ("000028", "粤新发展", "SZ"),
    ("000029", "深深宝A", "SZ"),
    ("000030", "深深宝B", "SZ"),
    ("000031", "中粮地产", "SZ"),
]

CONCEPTS = [
    "银行", "房地产", "汽车", "电力", "航运", "保险",
    "钢铁", "化工", "机械", "电子", "医药",
    "食品饮料", "纺织服装", "采矿", "建筑",
    "深圳板块", "上海板块", "沿海概念", "国企改革",
    "绿色能源", "新基建",
]

# ============ 股票-行业映射 ============

STOCK_INDUSTRIES = {
    # 上海（SH）股票
    "600000": "银行",        # 浦发银行
    "600004": "运输",        # 白云机场
    "600006": "综合类",      # 东方集团
    "600007": "建筑",        # 巨龙集团
    "600008": "房地产",      # 首创集团
    "600009": "运输",        # 上海机场
    "600010": "钢铁",        # 包钢股份
    "600011": "电力",        # 华能国际
    "600012": "运输",        # 皖通高速
    "600015": "银行",        # 华夏银行
    "600016": "银行",        # 民生银行
    "600017": "保险",        # 新华保险
    "600018": "运输",        # 上港集团
    "600019": "钢铁",        # 宝钢股份
    "600020": "运输",        # 中原高速
    "600021": "电力",        # 上海电力
    "600022": "钢铁",        # 山东钢铁
    "600023": "电力",        # 浙能电力
    "600025": "电力",        # 华能水电
    "600026": "运输",        # 中远海能
    # 深圳（SZ）股票
    "000001": "银行",        # 平安银行
    "000002": "房地产",      # 万科A
    "000004": "农业",        # 国农科技
    "000005": "房地产",      # 世纪星源
    "000006": "房地产",      # 深振业A
    "000007": "综合类",      # 全新好
    "000008": "机械",        # 神州高铁
    "000009": "综合类",      # 中国宝安
    "000010": "生态环保",    # 美丽生态
    "000011": "房地产",      # 深物业A
    "000012": "电子",        # 南玻A
    "000013": "医药",        # 一致药业
    "000014": "房地产",      # 宝安地产
    "000015": "电子",        # 深康佳A
    "000016": "房地产",      # 深中华A
    "000017": "房地产",      # 深中华B
    "000018": "综合类",      # 泛海控股
    "000019": "房地产",      # 深深房A
    "000020": "房地产",      # 深深房B
    "000021": "电子",        # 深科技
    "000022": "运输",        # 深赤湾A
    "000023": "运输",        # 深赤湾B
    "000024": "运输",        # 深高速
    "000025": "商业",        # 特力A
    "000026": "电子",        # 飞亚达A
    "000027": "电力",        # 深圳能源
    "000028": "房地产",      # 粤新发展
    "000029": "房地产",      # 深深宝A
    "000030": "房地产",      # 深深宝B
    "000031": "房地产",      # 中粮地产
}


# ============ 生成 CSV 文件 ============

def generate_csv_file(output_path="test-data/test_import_stocks_concepts.csv"):
    """生成测试 CSV 文件（股票-概念映射）"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # 写入表头
        writer.writerow([
            "股票代码", "股票名称", "全部页数", "热帖首页页阅读总数",
            "价格", "行业", "概念", "换手", "净流入"
        ])

        # 为每个股票写入 3-5 个概念映射
        for stock_code, stock_name, exchange_prefix in STOCKS:
            num_concepts = random.randint(3, 5)
            selected_concepts = random.sample(CONCEPTS, min(num_concepts, len(CONCEPTS)))

            # 从映射表中获取该股票的行业
            industry = STOCK_INDUSTRIES.get(stock_code, "其他")

            for concept in selected_concepts:
                writer.writerow([
                    stock_code,                          # 股票代码（保持字符串格式）
                    stock_name,                          # 股票名称
                    random.randint(1, 50),               # 全部页数
                    random.randint(1000, 100000),        # 热帖首页页阅读总数
                    f"{random.uniform(5, 50):.2f}",      # 价格
                    industry,                            # 行业（从映射表获取）
                    concept,                             # 概念
                    f"{random.uniform(0, 5):.2f}",       # 换手
                    random.randint(-1000000, 1000000),   # 净流入
                ])

    print(f"✅ CSV 文件已生成: {output_path}")
    print(f"   - 股票数: {len(STOCKS)}")
    print(f"   - 概念数: {len(CONCEPTS)}")
    with open(output_path, "r", encoding="utf-8") as f:
        rows = len(f.readlines()) - 1  # 减去表头
    print(f"   - 映射行数: {rows}")


# ============ 生成 TXT 文件 ============

def generate_txt_file(
    metric_code="EEE",
    start_date="2025-11-01",
    num_days=20,
    output_dir="test-data"
):
    """生成测试 TXT 文件（日期特定的指标数据）"""
    os.makedirs(output_dir, exist_ok=True)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    trading_dates = []

    # 生成交易日期（排除周末）
    current_dt = start_dt
    while len(trading_dates) < num_days:
        if current_dt.weekday() < 5:  # Monday=0, Friday=4
            trading_dates.append(current_dt)
        current_dt += timedelta(days=1)

    # 为每个交易日生成一个 TXT 文件
    file_paths = []
    for trade_date in trading_dates:
        date_str = trade_date.strftime("%Y-%m-%d")
        filename = f"{output_dir}/{metric_code}_{date_str}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            for stock_code, stock_name, exchange_prefix in STOCKS:
                # 生成股票代码（带前缀）
                full_code = f"{exchange_prefix}{stock_code}"

                # 生成指标值（随机）
                if metric_code == "EEE":
                    # 行业活跃度：较小的数值
                    value = random.randint(100000, 5000000)
                else:  # TTV
                    # 交易交易量：较大的数值
                    value = random.randint(1000000, 100000000)

                # 写入行（Tab 分隔）
                f.write(f"{full_code}\t{date_str}\t{value}\n")

        file_paths.append(filename)
        print(f"✅ TXT 文件已生成: {filename}")

    print(f"\n📊 {metric_code} 指标数据统计:")
    print(f"   - 日期范围: {trading_dates[0].strftime('%Y-%m-%d')} ~ {trading_dates[-1].strftime('%Y-%m-%d')}")
    print(f"   - 交易日数: {len(trading_dates)}")
    print(f"   - 股票数: {len(STOCKS)}")
    print(f"   - 总行数: {len(STOCKS) * len(trading_dates)}")

    return file_paths


# ============ 主程序 ============

if __name__ == "__main__":
    print("=" * 80)
    print("📝 测试数据生成脚本")
    print("=" * 80)

    # 生成 CSV 文件
    print("\n[1/3] 生成 CSV 文件...")
    generate_csv_file()

    # 生成 EEE 指标数据
    print("\n[2/3] 生成 EEE 指标数据...")
    generate_txt_file(metric_code="EEE", start_date="2025-11-01", num_days=20)

    # 生成 TTV 指标数据
    print("\n[3/3] 生成 TTV 指标数据...")
    generate_txt_file(metric_code="TTV", start_date="2025-11-01", num_days=20)

    print("\n" + "=" * 80)
    print("✨ 测试数据生成完成！")
    print("=" * 80)
    print("""
📋 使用说明：
1. CSV 文件用于定义股票-概念关系，需要先导入
   路径: test-data/test_import_stocks_concepts.csv

2. TXT 文件用于导入日期特定的指标数据
   EEE 指标: test-data/EEE_YYYY-MM-DD.txt (20 个文件)
   TTV 指标: test-data/TTV_YYYY-MM-DD.txt (20 个文件)

3. 导入顺序：
   第1步: 导入 CSV 文件
   第2步: 逐日导入 EEE 指标数据
   第3步: 逐日导入 TTV 指标数据

4. 验证步骤：
   - 检查 stocks 表：应有 50 个股票
   - 检查 concepts 表：应有 20+ 个概念
   - 检查 stock_concepts 表：应有 150+ 个映射关系
   - 检查 stock_metric_data_raw 表：应有 2000+ 条原始数据
   - 检查 concept_stock_daily_rank 表：应有排名数据
   - 检查 concept_daily_summary 表：应有汇总数据
""")
