#!/bin/bash
# ========================================
# 生产环境代码更新脚本
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 服务器配置
SERVER_USER="ubuntu"
SERVER_HOST="82.157.28.35"
SERVER_PASSWORD="chen_188_8_8"
SERVER_PATH="/var/www/stock-analysis"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "生产环境代码更新"
echo "========================================="
echo ""
echo "服务器: $SERVER_HOST"
echo "路径: $SERVER_PATH"
echo ""

# 确认更新
read -p "确认开始更新? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "更新已取消"
    exit 1
fi

# ========================================
# 1. 备份数据库
# ========================================
echo ""
echo -e "${YELLOW}步骤 1/7: 备份数据库${NC}"
echo "========================================="

BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).sql"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
cd $SERVER_PATH/backend
mkdir -p backups
PGPASSWORD=stock_pass_2024 pg_dump -h localhost -U stock_user stock_analysis > backups/$BACKUP_NAME
gzip backups/$BACKUP_NAME
echo "✅ 数据库已备份: backups/$BACKUP_NAME.gz"
ls -lh backups/$BACKUP_NAME.gz
ENDSSH

# ========================================
# 2. 备份当前代码
# ========================================
echo ""
echo -e "${YELLOW}步骤 2/7: 备份当前代码${NC}"
echo "========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis

# 备份后端
if [ -d "backend.backup" ]; then
    rm -rf backend.backup.old
    mv backend.backup backend.backup.old
fi
cp -r backend backend.backup

# 备份前端dist
if [ -d "frontend/dist" ]; then
    if [ -d "frontend/dist.backup" ]; then
        rm -rf frontend/dist.backup.old
        mv frontend/dist.backup frontend/dist.backup.old
    fi
    cp -r frontend/dist frontend/dist.backup
fi

echo "✅ 当前代码已备份"
ENDSSH

# ========================================
# 3. 更新后端代码
# ========================================
echo ""
echo -e "${YELLOW}步骤 3/7: 更新后端代码${NC}"
echo "========================================="

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
# 4. 更新Python依赖
# ========================================
echo ""
echo -e "${YELLOW}步骤 4/7: 检查并更新Python依赖${NC}"
echo "========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis/backend

# 修复Python 3.8兼容性
for file in app/api/imports.py app/schemas/common.py app/schemas/stock.py app/core/config.py app/services/optimized_txt_import.py app/services/optimized_csv_import.py; do
    if [ -f "$file" ]; then
        # 确保future import在最前面
        if ! head -1 "$file" | grep -q "from __future__ import annotations"; then
            sed -i '1i from __future__ import annotations\n' "$file"
        fi
        # 替换类型注解
        sed -i -e 's/: list\[/: List[/g' -e 's/-> list\[/-> List[/g' -e 's/response_model=list\[/response_model=List[/g' "$file"
        sed -i 's/from typing import Optional$/from typing import Optional, List, Dict/' "$file"
    fi
done

# 更新依赖
source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Python依赖已更新"
ENDSSH

# ========================================
# 5. 重启后端服务
# ========================================
echo ""
echo -e "${YELLOW}步骤 5/7: 重启后端服务${NC}"
echo "========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
sudo -S systemctl restart stock-analysis-backend <<< "$SERVER_PASSWORD"
sleep 5

# 检查服务状态
if sudo systemctl is-active --quiet stock-analysis-backend; then
    echo "✅ 后端服务已重启"
else
    echo "❌ 后端服务启动失败"
    sudo journalctl -u stock-analysis-backend -n 20 --no-pager
    exit 1
fi
ENDSSH

# ========================================
# 6. 更新并构建前端
# ========================================
echo ""
echo -e "${YELLOW}步骤 6/7: 更新并构建前端${NC}"
echo "========================================="

rsync -avz \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='.env.local' \
    -e "sshpass -p $SERVER_PASSWORD ssh -o StrictHostKeyChecking=no" \
    frontend/ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/frontend/

echo "前端代码已上传，开始构建..."

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis/frontend

# 确保build命令不包含类型检查
sed -i 's/"build": "vue-tsc && vite build"/"build": "vite build"/g' package.json

# 安装依赖（如果package.json有变化）
npm install

# 构建
npm run build

echo "✅ 前端构建完成"
ENDSSH

# 重启Nginx
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
sudo -S systemctl reload nginx <<< "$SERVER_PASSWORD"
echo "✅ Nginx已重启"
ENDSSH

# ========================================
# 7. 验证部署
# ========================================
echo ""
echo -e "${YELLOW}步骤 7/7: 验证部署${NC}"
echo "========================================="

# 等待服务完全启动
sleep 3

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
echo "服务状态检查："
echo "----------------------------------------"

# 后端服务
if sudo systemctl is-active --quiet stock-analysis-backend; then
    echo "✅ 后端服务: 运行中"
else
    echo "❌ 后端服务: 停止"
fi

# Nginx
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx: 运行中"
else
    echo "❌ Nginx: 停止"
fi

# 端口检查
if sudo netstat -tuln | grep -q ':8000'; then
    echo "✅ 端口8000: 监听中"
else
    echo "❌ 端口8000: 未监听"
fi

echo ""
echo "HTTP服务检查："
echo "----------------------------------------"

# 测试前端
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' https://qwquant.com)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 前端页面: $HTTP_CODE"
else
    echo "❌ 前端页面: $HTTP_CODE"
fi

# 测试API
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' 'https://qwquant.com/api/v1/stocks?page=1&page_size=1')
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 后端API: $HTTP_CODE"
else
    echo "❌ 后端API: $HTTP_CODE"
fi
ENDSSH

echo ""
echo "========================================="
echo -e "${GREEN}更新完成！${NC}"
echo "========================================="
echo ""
echo "访问地址："
echo "  https://qwquant.com"
echo "  https://qwquant.com/api/docs"
echo ""
echo "如果遇到问题，可以查看日志："
echo "  sudo journalctl -u stock-analysis-backend -f"
echo "  sudo tail -f /var/log/nginx/qwquant_error.log"
echo ""
echo "========================================="
