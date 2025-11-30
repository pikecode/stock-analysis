#!/bin/bash
# ========================================
# 仅更新后端服务
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SERVER_USER="ubuntu"
SERVER_HOST="82.157.28.35"
SERVER_PASSWORD="chen_188_8_8"
SERVER_PATH="/var/www/stock-analysis"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "更新后端服务"
echo "========================================="
echo ""

# ========================================
# 1. 备份数据库
# ========================================
echo -e "${YELLOW}步骤 1/4: 备份数据库${NC}"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).sql"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
cd $SERVER_PATH/backend
mkdir -p backups
PGPASSWORD=stock_pass_2024 pg_dump -h localhost -U stock_user stock_analysis > backups/$BACKUP_NAME
gzip backups/$BACKUP_NAME
echo "✅ 数据库已备份: backups/$BACKUP_NAME.gz"
ENDSSH

# ========================================
# 2. 上传后端代码
# ========================================
echo ""
echo -e "${YELLOW}步骤 2/4: 上传后端代码${NC}"
cd "$PROJECT_ROOT"

rsync -avz \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='*.db' \
    --exclude='data/' \
    --exclude='uploads/*' \
    --exclude='backups/' \
    -e "sshpass -p $SERVER_PASSWORD ssh -o StrictHostKeyChecking=no" \
    backend/ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/backend/

echo "✅ 后端代码已上传"

# ========================================
# 3. 更新依赖并修复兼容性
# ========================================
echo ""
echo -e "${YELLOW}步骤 3/4: 更新依赖${NC}"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis/backend

# 修复Python 3.8兼容性
find app -name "*.py" -type f -exec sed -i -e 's/: list\[/: List[/g' -e 's/-> list\[/-> List[/g' -e 's/response_model=list\[/response_model=List[/g' {} \;
find app -name "*.py" -type f -exec sed -i 's/from typing import Optional$/from typing import Optional, List, Dict/' {} \; 2>/dev/null || true

# 更新依赖
source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ 依赖已更新"
ENDSSH

# ========================================
# 4. 重启服务
# ========================================
echo ""
echo -e "${YELLOW}步骤 4/4: 重启后端服务${NC}"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
sudo -S systemctl restart stock-analysis-backend <<< "$SERVER_PASSWORD"
sleep 5

if sudo systemctl is-active --quiet stock-analysis-backend; then
    echo "✅ 后端服务已重启"

    # 测试API
    sleep 2
    HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/api/v1/stocks?page=1&page_size=1')
    if [ "\$HTTP_CODE" = "200" ]; then
        echo "✅ API测试通过: \$HTTP_CODE"
    else
        echo "⚠️  API返回: \$HTTP_CODE"
    fi
else
    echo "❌ 后端服务启动失败"
    sudo journalctl -u stock-analysis-backend -n 30 --no-pager
    exit 1
fi
ENDSSH

echo ""
echo "========================================="
echo -e "${GREEN}后端更新完成！${NC}"
echo "========================================="
echo ""
echo "API地址: https://qwquant.com/api/docs"
echo ""
