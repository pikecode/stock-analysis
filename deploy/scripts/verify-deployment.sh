#!/bin/bash
# ========================================
# 部署验证脚本
# ========================================

set -e

echo "========================================="
echo "股票分析系统 - 部署验证"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_service() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        echo -e "${GREEN}✓${NC} $service_name 运行正常"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name 未运行"
        return 1
    fi
}

check_port() {
    local port=$1
    local description=$2
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${GREEN}✓${NC} 端口 $port ($description) 正在监听"
        return 0
    else
        echo -e "${RED}✗${NC} 端口 $port ($description) 未监听"
        return 1
    fi
}

check_http() {
    local url=$1
    local description=$2
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $description 可访问 ($url)"
        return 0
    else
        echo -e "${RED}✗${NC} $description 无法访问 ($url)"
        return 1
    fi
}

check_directory() {
    local dir=$1
    local description=$2
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description 存在 ($dir)"
        return 0
    else
        echo -e "${RED}✗${NC} $description 不存在 ($dir)"
        return 1
    fi
}

check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description 存在 ($file)"
        return 0
    else
        echo -e "${RED}✗${NC} $description 不存在 ($file)"
        return 1
    fi
}

# 检查计数器
CHECKS_TOTAL=0
CHECKS_PASSED=0

run_check() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if "$@"; then
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        return 1
    fi
}

# 开始检查
echo "1. 系统服务检查"
echo "----------------------------------------"
run_check check_service "postgresql"
run_check check_service "nginx"
run_check check_service "stock-analysis-backend"
echo ""

echo "2. 端口监听检查"
echo "----------------------------------------"
run_check check_port "5432" "PostgreSQL"
run_check check_port "80" "Nginx HTTP"
run_check check_port "8000" "Backend API"
echo ""

echo "3. 目录结构检查"
echo "----------------------------------------"
run_check check_directory "/var/www/stock-analysis" "项目根目录"
run_check check_directory "/var/www/stock-analysis/backend" "后端目录"
run_check check_directory "/var/www/stock-analysis/frontend" "前端目录"
run_check check_directory "/var/www/stock-analysis/backend/venv" "Python虚拟环境"
run_check check_directory "/var/www/stock-analysis/frontend/dist" "前端构建目录"
echo ""

echo "4. 配置文件检查"
echo "----------------------------------------"
run_check check_file "/var/www/stock-analysis/backend/.env" "后端环境配置"
run_check check_file "/etc/nginx/sites-enabled/stock-analysis" "Nginx站点配置"
run_check check_file "/etc/systemd/system/stock-analysis-backend.service" "Systemd服务文件"
echo ""

echo "5. 数据库连接检查"
echo "----------------------------------------"
if PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 数据库连接正常"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))

    # 检查表是否存在
    TABLE_COUNT=$(PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | tr -d ' ')
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} 数据库表已创建 (共 $TABLE_COUNT 个表)"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} 数据库表未创建"
    fi
else
    echo -e "${RED}✗${NC} 数据库连接失败"
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 2))
echo ""

echo "6. HTTP服务检查"
echo "----------------------------------------"
# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "127.0.0.1")

run_check check_http "http://127.0.0.1:8000/api/v1/health" "后端健康检查"
run_check check_http "http://127.0.0.1:8000/docs" "API文档"
run_check check_http "http://127.0.0.1/" "Nginx前端"
echo ""

echo "7. Python虚拟环境检查"
echo "----------------------------------------"
if [ -f "/var/www/stock-analysis/backend/venv/bin/python" ]; then
    PYTHON_VERSION=$(/var/www/stock-analysis/backend/venv/bin/python --version 2>&1)
    echo -e "${GREEN}✓${NC} Python虚拟环境正常 ($PYTHON_VERSION)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))

    # 检查关键依赖
    if /var/www/stock-analysis/backend/venv/bin/pip list 2>/dev/null | grep -q "fastapi"; then
        echo -e "${GREEN}✓${NC} FastAPI 已安装"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} FastAPI 未安装"
    fi

    if /var/www/stock-analysis/backend/venv/bin/pip list 2>/dev/null | grep -q "sqlalchemy"; then
        echo -e "${GREEN}✓${NC} SQLAlchemy 已安装"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} SQLAlchemy 未安装"
    fi
else
    echo -e "${RED}✗${NC} Python虚拟环境不存在"
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 3))
echo ""

echo "8. 日志文件检查"
echo "----------------------------------------"
if [ -f "/var/log/nginx/stock-analysis.access.log" ]; then
    ACCESS_LOG_SIZE=$(du -h /var/log/nginx/stock-analysis.access.log | cut -f1)
    echo -e "${GREEN}✓${NC} Nginx访问日志存在 (大小: $ACCESS_LOG_SIZE)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} Nginx访问日志不存在（可能尚未有访问）"
fi

if [ -f "/var/log/nginx/stock-analysis.error.log" ]; then
    ERROR_LOG_SIZE=$(du -h /var/log/nginx/stock-analysis.error.log | cut -f1)
    echo -e "${GREEN}✓${NC} Nginx错误日志存在 (大小: $ERROR_LOG_SIZE)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} Nginx错误日志不存在"
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 2))
echo ""

# 总结
echo "========================================="
echo "验证总结"
echo "========================================="
PASS_RATE=$((CHECKS_PASSED * 100 / CHECKS_TOTAL))

if [ $PASS_RATE -eq 100 ]; then
    echo -e "${GREEN}✓ 所有检查通过！ ($CHECKS_PASSED/$CHECKS_TOTAL)${NC}"
    EXIT_CODE=0
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠ 大部分检查通过 ($CHECKS_PASSED/$CHECKS_TOTAL - $PASS_RATE%)${NC}"
    echo -e "${YELLOW}  建议检查失败项${NC}"
    EXIT_CODE=1
else
    echo -e "${RED}✗ 多项检查失败 ($CHECKS_PASSED/$CHECKS_TOTAL - $PASS_RATE%)${NC}"
    echo -e "${RED}  请检查部署日志并修复问题${NC}"
    EXIT_CODE=2
fi

echo ""
echo "访问地址："
echo "  前端: http://$SERVER_IP"
echo "  API文档: http://$SERVER_IP/api/docs"
echo "  管理后台: http://$SERVER_IP/admin"
echo ""

if [ $EXIT_CODE -ne 0 ]; then
    echo "故障排查："
    echo "  查看后端日志: sudo journalctl -u stock-analysis-backend -n 50"
    echo "  查看Nginx日志: sudo tail -f /var/log/nginx/stock-analysis.error.log"
    echo "  测试数据库: psql -h localhost -U stock_user -d stock_analysis"
    echo ""
fi

echo "========================================="

exit $EXIT_CODE
