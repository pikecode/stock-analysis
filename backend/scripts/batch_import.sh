#!/bin/bash

###############################################################################
# 批量导入脚本 - 用于一次性导入多个文件
#
# 用法：
#   ./batch_import.sh <数据目录> [--csv-only] [--txt-only] [--verbose]
#
# 例子：
#   ./batch_import.sh /data/stock
#   ./batch_import.sh /data/stock --csv-only
#   ./batch_import.sh /data/stock --txt-only --verbose
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本参数
DATA_DIR="${1:-.}"
CSV_ONLY=false
TXT_ONLY=false
VERBOSE=false

# 解析参数
for arg in "$@"; do
    case $arg in
        --csv-only)
            CSV_ONLY=true
            TXT_ONLY=false
            ;;
        --txt-only)
            TXT_ONLY=true
            CSV_ONLY=false
            ;;
        --verbose)
            VERBOSE=true
            ;;
    esac
done

# 检查数据目录
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${RED}❌ 错误：目录不存在 $DATA_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  股票分析系统 - 批量数据导入${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "数据目录: ${YELLOW}$DATA_DIR${NC}"
echo -e "CSV导入: ${YELLOW}$([[ $CSV_ONLY == true ]] && echo '仅CSV' || echo '启用')${NC}"
echo -e "TXT导入: ${YELLOW}$([[ $TXT_ONLY == true ]] && echo '仅TXT' || echo '启用')${NC}"
echo -e "详细输出: ${YELLOW}$([[ $VERBOSE == true ]] && echo '是' || echo '否')${NC}"
echo ""

# 统计
total_files=0
success_files=0
failed_files=0

# 导入选项
IMPORT_OPTS=""
if [ "$VERBOSE" == "true" ]; then
    IMPORT_OPTS="$IMPORT_OPTS --verbose"
fi

###############################################################################
# CSV文件导入
###############################################################################

if [ "$TXT_ONLY" == "false" ]; then
    echo -e "${BLUE}→ 开始导入CSV文件${NC}"

    csv_count=0
    for csv_file in "$DATA_DIR"/*.csv; do
        if [ -f "$csv_file" ]; then
            csv_count=$((csv_count + 1))
            total_files=$((total_files + 1))

            filename=$(basename "$csv_file")
            echo -n "  [$csv_count] 导入 $filename ... "

            if python scripts/direct_import.py "$csv_file" --type CSV $IMPORT_OPTS 2>&1 > /tmp/import.log; then
                echo -e "${GREEN}✓${NC}"
                success_files=$((success_files + 1))
            else
                echo -e "${RED}✗${NC}"
                failed_files=$((failed_files + 1))
                if [ "$VERBOSE" == "true" ]; then
                    cat /tmp/import.log
                fi
            fi
        fi
    done

    if [ $csv_count -eq 0 ]; then
        echo -e "  ${YELLOW}没有找到CSV文件${NC}"
    else
        echo ""
    fi
fi

###############################################################################
# TXT文件导入
###############################################################################

if [ "$CSV_ONLY" == "false" ]; then
    echo -e "${BLUE}→ 开始导入TXT文件${NC}"

    # 检测指标类型（从文件名）
    txt_count=0
    for txt_file in "$DATA_DIR"/*.txt; do
        if [ -f "$txt_file" ]; then
            txt_count=$((txt_count + 1))
            total_files=$((total_files + 1))

            filename=$(basename "$txt_file")
            echo -n "  [$txt_count] 导入 $filename ... "

            # 自动识别指标代码（从文件名提取）
            # 支持格式：ttv_20240101.txt, ttv.txt, TTV_xxx.txt 等
            metric_code=$(echo "$filename" | sed 's/[._].*//' | tr '[:lower:]' '[:upper:]')

            # 仅保留字母部分
            metric_code=$(echo "$metric_code" | sed 's/[^A-Z]//g')

            if [ -z "$metric_code" ]; then
                echo -e "${RED}✗${NC} (无法识别指标代码)"
                failed_files=$((failed_files + 1))
                continue
            fi

            if python scripts/direct_import.py "$txt_file" --type TXT --metric-code "$metric_code" $IMPORT_OPTS 2>&1 > /tmp/import.log; then
                echo -e "${GREEN}✓${NC}"
                success_files=$((success_files + 1))
            else
                echo -e "${RED}✗${NC}"
                failed_files=$((failed_files + 1))
                if [ "$VERBOSE" == "true" ]; then
                    cat /tmp/import.log
                fi
            fi
        fi
    done

    if [ $txt_count -eq 0 ]; then
        echo -e "  ${YELLOW}没有找到TXT文件${NC}"
    else
        echo ""
    fi
fi

###############################################################################
# 总结
###############################################################################

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  导入汇总${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "总文件数: ${YELLOW}$total_files${NC}"
echo -e "成功: ${GREEN}$success_files${NC}"
echo -e "失败: ${RED}$failed_files${NC}"

if [ $failed_files -eq 0 ] && [ $total_files -gt 0 ]; then
    echo -e ""
    echo -e "${GREEN}✅ 所有文件导入成功！${NC}"
    exit 0
elif [ $total_files -eq 0 ]; then
    echo -e ""
    echo -e "${YELLOW}⚠️  未找到任何数据文件${NC}"
    exit 1
else
    echo -e ""
    echo -e "${RED}❌ 部分文件导入失败${NC}"
    exit 1
fi
