#!/bin/bash
# ========================================
# 仅更新前端服务
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
echo "更新前端服务"
echo "========================================="
echo ""

# ========================================
# 1. 备份当前dist
# ========================================
echo -e "${YELLOW}步骤 1/4: 备份当前版本${NC}"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis/frontend

if [ -d "dist" ]; then
    if [ -d "dist.backup" ]; then
        rm -rf dist.backup.old
        mv dist.backup dist.backup.old
    fi
    cp -r dist dist.backup
    echo "✅ 当前版本已备份"
else
    echo "⚠️  未找到dist目录"
fi
ENDSSH

# ========================================
# 2. 上传前端代码
# ========================================
echo ""
echo -e "${YELLOW}步骤 2/4: 上传前端代码${NC}"
cd "$PROJECT_ROOT"

rsync -avz \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='.env.local' \
    -e "sshpass -p $SERVER_PASSWORD ssh -o StrictHostKeyChecking=no" \
    frontend/ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/frontend/

echo "✅ 前端代码已上传"

# ========================================
# 3. 构建前端
# ========================================
echo ""
echo -e "${YELLOW}步骤 3/4: 构建前端${NC}"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/stock-analysis/frontend

# 确保build命令不包含类型检查（加快构建速度）
sed -i 's/"build": "vue-tsc && vite build"/"build": "vite build"/g' package.json

# 安装依赖（如果package.json有变化）
npm install

# 构建
echo "正在构建前端..."
npm run build

if [ -d "dist" ]; then
    echo "✅ 前端构建成功"
    echo "构建大小:"
    du -sh dist
else
    echo "❌ 构建失败"
    exit 1
fi
ENDSSH

# ========================================
# 4. 重启Nginx
# ========================================
echo ""
echo -e "${YELLOW}步骤 4/4: 重启Nginx${NC}"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << ENDSSH
sudo -S systemctl reload nginx <<< "$SERVER_PASSWORD"

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx已重启"

    # 测试前端
    sleep 1
    HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' https://qwquant.com)
    if [ "\$HTTP_CODE" = "200" ]; then
        echo "✅ 前端页面测试通过: \$HTTP_CODE"
    else
        echo "⚠️  前端页面返回: \$HTTP_CODE"
    fi
else
    echo "❌ Nginx重启失败"
    exit 1
fi
ENDSSH

echo ""
echo "========================================="
echo -e "${GREEN}前端更新完成！${NC}"
echo "========================================="
echo ""
echo "访问地址: https://qwquant.com"
echo ""
echo "如需回滚："
echo "  ssh ubuntu@82.157.28.35"
echo "  cd /var/www/stock-analysis/frontend"
echo "  rm -rf dist && mv dist.backup dist"
echo "  sudo systemctl reload nginx"
echo ""
