#!/bin/bash
# ========================================
# 创建部署包脚本
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PACKAGE_DIR="$PROJECT_ROOT/deploy-package"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="stock-analysis-deploy-$TIMESTAMP.tar.gz"

echo "========================================="
echo "创建部署包"
echo "========================================="

# 清理旧的打包目录
if [ -d "$PACKAGE_DIR" ]; then
    echo "清理旧的打包目录..."
    rm -rf "$PACKAGE_DIR"
fi

# 创建打包目录结构
echo "创建打包目录结构..."
mkdir -p "$PACKAGE_DIR"/{backend,frontend,deploy}

# 复制后端文件
echo "复制后端文件..."
rsync -a \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='*.db' \
    --exclude='data/' \
    "$PROJECT_ROOT/backend/" \
    "$PACKAGE_DIR/backend/"

# 复制前端文件
echo "复制前端文件..."
rsync -a \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='.env.local' \
    "$PROJECT_ROOT/frontend/" \
    "$PACKAGE_DIR/frontend/"

# 复制部署脚本和文档
echo "复制部署脚本..."
rsync -a \
    "$PROJECT_ROOT/deploy/" \
    "$PACKAGE_DIR/deploy/"

# 创建部署说明文件
cat > "$PACKAGE_DIR/DEPLOY-INSTRUCTIONS.txt" << 'EOF'
========================================
股票分析系统部署包
========================================

本部署包包含：
1. backend/      - 后端代码 (FastAPI)
2. frontend/     - 前端代码 (Vue 3)
3. deploy/       - 部署脚本和文档

部署步骤：
----------------------------------------

1. 上传部署包到服务器
   scp stock-analysis-deploy-*.tar.gz ubuntu@your-server:/tmp/

2. 解压部署包
   cd /tmp
   tar -xzf stock-analysis-deploy-*.tar.gz
   cd stock-analysis-deploy-*

3. 执行部署脚本
   cd deploy/scripts
   chmod +x *.sh
   ./00-deploy-all.sh

4. 部署后配置
   - 修改数据库密码
   - 创建管理员账户
   - 配置域名和SSL

详细说明：
----------------------------------------
请查看 deploy/docs/DEPLOYMENT.md

服务管理：
----------------------------------------
# 后端服务
sudo systemctl status stock-analysis-backend
sudo systemctl restart stock-analysis-backend

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx

访问地址：
----------------------------------------
- 前端: http://服务器IP
- API文档: http://服务器IP/api/docs
- 管理后台: http://服务器IP/admin

========================================
EOF

# 创建版本信息文件
cat > "$PACKAGE_DIR/VERSION.txt" << EOF
========================================
版本信息
========================================
打包时间: $(date '+%Y-%m-%d %H:%M:%S')
Git分支: $(cd "$PROJECT_ROOT" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Git提交: $(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
打包机器: $(hostname)
打包用户: $(whoami)
========================================
EOF

# 创建压缩包
echo ""
echo "创建压缩包..."
cd "$(dirname "$PACKAGE_DIR")"
tar -czf "$PACKAGE_NAME" "$(basename "$PACKAGE_DIR")"

# 显示打包结果
echo ""
echo "========================================="
echo "打包完成！"
echo "========================================="
echo "部署包位置: $(dirname "$PACKAGE_DIR")/$PACKAGE_NAME"
echo "部署包大小: $(du -h "$(dirname "$PACKAGE_DIR")/$PACKAGE_NAME" | cut -f1)"
echo ""
echo "上传命令示例："
echo "scp $(dirname "$PACKAGE_DIR")/$PACKAGE_NAME ubuntu@your-server:/tmp/"
echo ""
echo "解压命令："
echo "tar -xzf /tmp/$PACKAGE_NAME -C /tmp/"
echo ""
echo "部署命令："
echo "cd /tmp/$(basename "$PACKAGE_DIR")/deploy/scripts && ./00-deploy-all.sh"
echo "========================================="

# 清理临时目录
echo ""
read -p "是否清理临时打包目录? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$PACKAGE_DIR"
    echo "临时目录已清理"
fi

echo ""
echo "部署包创建成功！"
