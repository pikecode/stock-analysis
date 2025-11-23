#!/bin/bash
# =================================
# Stock Analysis - 一键部署脚本
# =================================
# 用法: sudo ./deploy.sh [install|update|start|stop|status]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_NAME="stock-analysis"
APP_DIR="/opt/stock-analysis"
LOG_DIR="/var/log/stock-analysis"
APP_USER="www-data"
PYTHON_VERSION="python3.11"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# =================================
# Helper Functions
# =================================

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════╗"
    echo "║    Stock Analysis - 原生部署               ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}请使用 root 权限运行: sudo $0${NC}"
        exit 1
    fi
}

check_deps() {
    local missing=0
    for cmd in $PYTHON_VERSION node psql redis-server nginx; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}缺少依赖: $cmd${NC}"
            missing=1
        fi
    done
    if [ $missing -eq 1 ]; then
        echo -e "${YELLOW}请先运行: sudo ./install-deps.sh${NC}"
        exit 1
    fi
}

# =================================
# Install Command
# =================================

cmd_install() {
    print_header
    check_root
    check_deps

    echo -e "${YELLOW}开始安装 Stock Analysis...${NC}"
    echo ""

    # [1] Create directories
    echo -e "${BLUE}[1/8] 创建目录结构...${NC}"
    mkdir -p $APP_DIR/{backend,frontend,uploads}
    mkdir -p $LOG_DIR
    chown -R $APP_USER:$APP_USER $APP_DIR $LOG_DIR
    echo -e "  ✓ 目录创建完成"

    # [2] Copy source code
    echo -e "${BLUE}[2/8] 复制源代码...${NC}"
    cp -r $SOURCE_DIR/backend/* $APP_DIR/backend/
    cp -r $SOURCE_DIR/frontend/* $APP_DIR/frontend/
    cp -r $SOURCE_DIR/docs $APP_DIR/
    echo -e "  ✓ 源代码复制完成"

    # [3] Create environment file
    echo -e "${BLUE}[3/8] 创建配置文件...${NC}"
    if [ ! -f "$APP_DIR/.env" ]; then
        DB_PASSWORD=$(openssl rand -hex 16)
        SECRET_KEY=$(openssl rand -hex 32)

        cat > $APP_DIR/.env << EOF
# Database
DATABASE_URL=postgresql://stock_user:${DB_PASSWORD}@localhost:5432/stock_analysis
DB_PASSWORD=${DB_PASSWORD}

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
SECRET_KEY=${SECRET_KEY}
DEBUG=false

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7
EOF
        chmod 600 $APP_DIR/.env
        echo -e "  ✓ 配置文件创建完成"
    else
        echo -e "  - 配置文件已存在，跳过"
    fi

    # [4] Setup Python environment
    echo -e "${BLUE}[4/8] 配置 Python 环境...${NC}"
    cd $APP_DIR/backend
    $PYTHON_VERSION -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt gunicorn
    deactivate
    echo -e "  ✓ Python 环境配置完成"

    # [5] Build frontend
    echo -e "${BLUE}[5/8] 构建前端...${NC}"
    cd $APP_DIR/frontend
    npm install
    npm run build
    echo -e "  ✓ 前端构建完成"

    # [6] Setup database
    echo -e "${BLUE}[6/8] 配置数据库...${NC}"
    source $APP_DIR/.env

    # Create database user and database
    sudo -u postgres psql -c "CREATE USER stock_user WITH PASSWORD '${DB_PASSWORD}';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE stock_analysis OWNER stock_user;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stock_analysis TO stock_user;" 2>/dev/null || true

    # Initialize tables
    if [ -f "$APP_DIR/docs/sql/init_tables.sql" ]; then
        sudo -u postgres psql -d stock_analysis -f $APP_DIR/docs/sql/init_tables.sql 2>/dev/null || true
    fi

    # Create admin user
    ADMIN_HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4EnALGSq6D.9FKie'
    sudo -u postgres psql -d stock_analysis << EOF
INSERT INTO users (username, email, password_hash, status)
VALUES ('admin', 'admin@localhost', '${ADMIN_HASH}', 'active')
ON CONFLICT (username) DO NOTHING;

INSERT INTO roles (name, description)
VALUES ('admin', '系统管理员')
ON CONFLICT (name) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO metric_types (code, name, file_pattern)
VALUES ('TTV', '总交易额', 'TTV'), ('EEE', '有效交易额', 'EEE')
ON CONFLICT (code) DO NOTHING;
EOF
    echo -e "  ✓ 数据库配置完成"

    # [7] Install systemd services
    echo -e "${BLUE}[7/8] 安装系统服务...${NC}"
    cp $SCRIPT_DIR/systemd/*.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable stock-analysis-api stock-analysis-celery stock-analysis-celery-beat
    echo -e "  ✓ 系统服务安装完成"

    # [8] Configure Nginx
    echo -e "${BLUE}[8/8] 配置 Nginx...${NC}"
    cp $SCRIPT_DIR/nginx/stock-analysis.conf /etc/nginx/sites-available/stock-analysis
    ln -sf /etc/nginx/sites-available/stock-analysis /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
    nginx -t && systemctl reload nginx
    echo -e "  ✓ Nginx 配置完成"

    # Set permissions
    chown -R $APP_USER:$APP_USER $APP_DIR $LOG_DIR

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  安装完成！${NC}"
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}启动服务: sudo $0 start${NC}"
}

# =================================
# Update Command
# =================================

cmd_update() {
    print_header
    check_root

    echo -e "${YELLOW}更新 Stock Analysis...${NC}"

    # Stop services
    cmd_stop

    # Update source code
    echo -e "${BLUE}[1/4] 更新源代码...${NC}"
    cp -r $SOURCE_DIR/backend/* $APP_DIR/backend/
    cp -r $SOURCE_DIR/frontend/* $APP_DIR/frontend/
    echo -e "  ✓ 源代码更新完成"

    # Update Python dependencies
    echo -e "${BLUE}[2/4] 更新 Python 依赖...${NC}"
    cd $APP_DIR/backend
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    echo -e "  ✓ Python 依赖更新完成"

    # Rebuild frontend
    echo -e "${BLUE}[3/4] 重新构建前端...${NC}"
    cd $APP_DIR/frontend
    npm install
    npm run build
    echo -e "  ✓ 前端构建完成"

    # Set permissions
    echo -e "${BLUE}[4/4] 设置权限...${NC}"
    chown -R $APP_USER:$APP_USER $APP_DIR
    echo -e "  ✓ 权限设置完成"

    # Start services
    cmd_start

    echo -e "${GREEN}更新完成！${NC}"
}

# =================================
# Start/Stop/Status Commands
# =================================

cmd_start() {
    print_header
    check_root

    echo -e "${YELLOW}启动服务...${NC}"
    systemctl start stock-analysis-api
    systemctl start stock-analysis-celery
    systemctl start stock-analysis-celery-beat

    sleep 3
    cmd_status
}

cmd_stop() {
    echo -e "${YELLOW}停止服务...${NC}"
    systemctl stop stock-analysis-api 2>/dev/null || true
    systemctl stop stock-analysis-celery 2>/dev/null || true
    systemctl stop stock-analysis-celery-beat 2>/dev/null || true
    echo -e "${GREEN}服务已停止${NC}"
}

cmd_restart() {
    check_root
    cmd_stop
    sleep 2
    cmd_start
}

cmd_status() {
    print_header
    echo -e "${BLUE}服务状态:${NC}"
    echo ""

    for service in stock-analysis-api stock-analysis-celery stock-analysis-celery-beat; do
        if systemctl is-active --quiet $service; then
            echo -e "  ✓ $service: ${GREEN}运行中${NC}"
        else
            echo -e "  ✗ $service: ${RED}已停止${NC}"
        fi
    done

    echo ""

    # Health check
    if curl -s http://localhost/health 2>/dev/null | grep -q "healthy"; then
        echo -e "  ✓ API 健康检查: ${GREEN}通过${NC}"
    else
        echo -e "  ✗ API 健康检查: ${RED}失败${NC}"
    fi

    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo "  网站: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo -e "${BLUE}默认账户:${NC}"
    echo "  用户名: admin"
    echo "  密码:   admin123"
}

cmd_logs() {
    local service=${1:-api}
    case $service in
        api)
            tail -f $LOG_DIR/api.log
            ;;
        celery)
            tail -f $LOG_DIR/celery.log
            ;;
        all)
            tail -f $LOG_DIR/*.log
            ;;
        *)
            echo "Usage: $0 logs [api|celery|all]"
            ;;
    esac
}

# =================================
# Main
# =================================

case "${1:-}" in
    install)
        cmd_install
        ;;
    update)
        cmd_update
        ;;
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "$2"
        ;;
    *)
        print_header
        echo "用法: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  install   首次安装"
        echo "  update    更新部署"
        echo "  start     启动服务"
        echo "  stop      停止服务"
        echo "  restart   重启服务"
        echo "  status    查看状态"
        echo "  logs      查看日志 [api|celery|all]"
        exit 1
        ;;
esac
