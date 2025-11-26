#!/bin/bash
# 股票分析系统 - 快速命令集合
# 使用方法: source quick_commands.sh 或 . quick_commands.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Users/peakom/work/stock-analysis"

# ========== 导入命令 ==========

# CSV导入
import_csv() {
    echo -e "${GREEN}导入CSV文件（股票-概念映射）${NC}"
    if [ -z "$1" ]; then
        echo -e "${RED}用法: import_csv <csv文件路径>${NC}"
        return 1
    fi
    python "$PROJECT_ROOT/imports/direct_import.py" "$1" --type CSV
}

# TXT单文件导入
import_txt() {
    echo -e "${GREEN}导入TXT文件（交易数据）${NC}"
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}用法: import_txt <txt文件路径> <指标代码>${NC}"
        echo -e "${YELLOW}示例: import_txt data.txt EEE${NC}"
        return 1
    fi
    python "$PROJECT_ROOT/imports/direct_import.py" "$1" --type TXT --metric-code "$2"
}

# TXT批量导入
batch_import() {
    echo -e "${GREEN}批量导入TXT文件（多日期）${NC}"
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}用法: batch_import <txt文件路径> <指标代码> [并行数]${NC}"
        echo -e "${YELLOW}示例: batch_import large.txt EEE 8${NC}"
        return 1
    fi
    local parallel=${3:-4}
    python "$PROJECT_ROOT/imports/batch_import.py" "$1" --metric-code "$2" --parallel "$parallel"
}

# 继续导入（断点续传）
resume_import() {
    echo -e "${GREEN}继续上次中断的导入${NC}"
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}用法: resume_import <txt文件路径> <指标代码> [并行数]${NC}"
        return 1
    fi
    local parallel=${3:-4}
    python "$PROJECT_ROOT/imports/batch_import.py" "$1" --metric-code "$2" --parallel "$parallel" --resume
}

# ========== 数据库命令 ==========

# 创建分区表
create_partitions() {
    echo -e "${GREEN}创建数据库分区表${NC}"
    psql -U peakom -d stock_analysis -f "$PROJECT_ROOT/database/scripts/01_create_partitions.sql"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 分区表创建成功${NC}"
    else
        echo -e "${RED}✗ 分区表创建失败${NC}"
        return 1
    fi
}

# 优化索引
optimize_indexes() {
    echo -e "${GREEN}优化数据库索引${NC}"
    psql -U peakom -d stock_analysis -f "$PROJECT_ROOT/database/scripts/02_optimize_indexes.sql"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 索引优化成功${NC}"
    else
        echo -e "${RED}✗ 索引优化失败${NC}"
        return 1
    fi
}

# 查看导入统计
import_stats() {
    echo -e "${GREEN}查看导入数据统计${NC}"
    psql -U peakom -d stock_analysis << EOF
SELECT
    metric_code as 指标,
    MIN(trade_date) as 开始日期,
    MAX(trade_date) as 结束日期,
    COUNT(DISTINCT trade_date) as 天数,
    COUNT(DISTINCT stock_code) as 股票数,
    COUNT(*) as 记录数
FROM concept_stock_daily_rank
GROUP BY metric_code
ORDER BY metric_code;
EOF
}

# 查看最近导入批次
recent_imports() {
    echo -e "${GREEN}最近的导入批次${NC}"
    psql -U peakom -d stock_analysis << EOF
SELECT
    id,
    file_name as 文件名,
    status as 状态,
    total_rows as 总行数,
    success_rows as 成功,
    error_rows as 失败,
    created_at as 创建时间
FROM import_batches
ORDER BY created_at DESC
LIMIT 10;
EOF
}

# 清理测试数据
clean_test_data() {
    echo -e "${YELLOW}清理测试数据${NC}"
    read -p "确定要清理所有TEST数据吗？(y/n): " confirm
    if [ "$confirm" = "y" ]; then
        psql -U peakom -d stock_analysis << EOF
DELETE FROM concept_stock_daily_rank WHERE metric_code = 'TEST';
DELETE FROM stock_metric_data_raw WHERE metric_code = 'TEST';
DELETE FROM import_batches WHERE file_name LIKE '%TEST%' OR file_name LIKE '%test%';
EOF
        echo -e "${GREEN}测试数据已清理${NC}"
    fi
}

# ========== 进度管理 ==========

# 查看导入进度
check_progress() {
    local metric=${1:-EEE}
    echo -e "${GREEN}查看 $metric 的导入进度${NC}"
    if [ -f "/tmp/batch_import_${metric}.json" ]; then
        cat "/tmp/batch_import_${metric}.json" | python -m json.tool
    else
        echo -e "${YELLOW}没有找到 $metric 的进度文件${NC}"
    fi
}

# 清理进度文件
clear_progress() {
    local metric=${1:-EEE}
    echo -e "${YELLOW}清理 $metric 的进度文件${NC}"
    rm -f "/tmp/batch_import_${metric}.json"
    echo -e "${GREEN}进度文件已清理${NC}"
}

# ========== 快捷操作 ==========

# 快速测试导入
test_import() {
    echo -e "${GREEN}创建测试文件并导入${NC}"
    cat > /tmp/test_import.txt << EOF
600000	2024-11-20	1000000
600001	2024-11-20	1500000
000001	2024-11-21	2000000
000002	2024-11-21	2500000
EOF
    python "$PROJECT_ROOT/imports/direct_import.py" /tmp/test_import.txt --type TXT --metric-code TEST
}

# 显示帮助
show_help() {
    echo -e "${BLUE}=============== 股票分析系统快速命令 ===============${NC}"
    echo ""
    echo -e "${YELLOW}导入命令:${NC}"
    echo "  import_csv <file>              - 导入CSV文件"
    echo "  import_txt <file> <code>       - 导入TXT文件"
    echo "  batch_import <file> <code> [n] - 批量导入（n个进程）"
    echo "  resume_import <file> <code>    - 继续中断的导入"
    echo ""
    echo -e "${YELLOW}数据库命令:${NC}"
    echo "  create_partitions              - 创建分区表"
    echo "  optimize_indexes               - 优化索引"
    echo "  import_stats                   - 查看导入统计"
    echo "  recent_imports                 - 查看最近批次"
    echo "  clean_test_data                - 清理测试数据"
    echo ""
    echo -e "${YELLOW}进度管理:${NC}"
    echo "  check_progress [code]          - 查看进度"
    echo "  clear_progress [code]          - 清理进度"
    echo ""
    echo -e "${YELLOW}其他:${NC}"
    echo "  test_import                    - 快速测试"
    echo "  show_help                      - 显示帮助"
    echo ""
    echo -e "${BLUE}示例:${NC}"
    echo "  import_csv /path/to/stock.csv"
    echo "  import_txt /path/to/trade.txt EEE"
    echo "  batch_import /path/to/large.txt EEE 8"
    echo ""
}

# 初始化提示
echo -e "${BLUE}股票分析系统快速命令已加载！${NC}"
echo -e "${YELLOW}输入 show_help 查看所有命令${NC}"
echo ""

# 导出函数
export -f import_csv
export -f import_txt
export -f batch_import
export -f resume_import
export -f create_partitions
export -f optimize_indexes
export -f import_stats
export -f recent_imports
export -f clean_test_data
export -f check_progress
export -f clear_progress
export -f test_import
export -f show_help