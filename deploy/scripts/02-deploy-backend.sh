#!/bin/bash
# ========================================
# 后端部署脚本
# ========================================

set -e

# 配置变量
PROJECT_DIR="/var/www/stock-analysis"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"
SERVICE_NAME="stock-analysis-backend"

echo "========================================="
echo "开始部署后端服务..."
echo "========================================="

# 1. 创建项目目录
echo "步骤 1/7: 创建项目目录..."
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR

# 2. 复制后端代码
echo "步骤 2/7: 复制后端代码..."
rsync -av --delete \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='venv' \
    --exclude='.env' \
    ../../backend/ $BACKEND_DIR/

# 3. 创建虚拟环境
echo "步骤 3/7: 创建 Python 虚拟环境..."
python3 -m venv $VENV_DIR

# 4. 安装依赖
echo "步骤 4/7: 安装 Python 依赖..."
$VENV_DIR/bin/pip install --upgrade pip
$VENV_DIR/bin/pip install -r $BACKEND_DIR/requirements.txt

# 5. 创建.env文件
echo "步骤 5/7: 创建环境配置文件..."
cat > $BACKEND_DIR/.env << 'EOF'
DATABASE_URL=postgresql://stock_user:stock_pass_2024@localhost:5432/stock_analysis
SECRET_KEY=your-secret-key-change-this-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
DEBUG=False
EOF

# 6. 创建systemd服务
echo "步骤 6/7: 创建系统服务..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Stock Analysis Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 7. 启动服务
echo "步骤 7/7: 启动后端服务..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# 等待服务启动
sleep 3

# 检查服务状态
echo ""
echo "========================================="
echo "检查服务状态..."
sudo systemctl status $SERVICE_NAME --no-pager || true

echo ""
echo "========================================="
echo "后端部署完成！"
echo "========================================="
echo "项目目录: $BACKEND_DIR"
echo "服务名称: $SERVICE_NAME"
echo "服务端口: 8000"
echo "========================================="
