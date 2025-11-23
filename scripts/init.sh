#!/bin/bash
# =================================
# Stock Analysis - 本地初始化脚本
# =================================
# 用于本地开发环境初始化（macOS / Linux）

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║     Stock Analysis - 本地初始化            ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$PROJECT_DIR"

# =================================
# 1. 环境检查
# =================================
echo -e "${YELLOW}[1/7] 检查运行环境...${NC}"

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "  ✓ $1 已安装"
        return 0
    else
        echo -e "  ${RED}✗ $1 未安装${NC}"
        return 1
    fi
}

MISSING_DEPS=0

# Check Python
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo -e "  ✓ Python 3.11 已安装"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$PYTHON_VERSION" == "3.10" || "$PYTHON_VERSION" == "3.11" || "$PYTHON_VERSION" == "3.12" ]]; then
        PYTHON_CMD="python3"
        echo -e "  ✓ Python $PYTHON_VERSION 已安装"
    else
        echo -e "  ${RED}✗ Python 3.10+ 未安装${NC}"
        MISSING_DEPS=1
    fi
else
    echo -e "  ${RED}✗ Python 未安装${NC}"
    MISSING_DEPS=1
fi

check_command "node" || MISSING_DEPS=1
check_command "npm" || MISSING_DEPS=1
check_command "psql" || MISSING_DEPS=1
check_command "redis-cli" || MISSING_DEPS=1

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}请先安装缺失的依赖：${NC}"
    echo ""
    echo "macOS (使用 Homebrew):"
    echo "  brew install python@3.11 node postgresql@15 redis"
    echo "  brew services start postgresql@15"
    echo "  brew services start redis"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt install python3.11 python3.11-venv nodejs npm postgresql redis-server"
    echo ""
    exit 1
fi

# Check PostgreSQL is running
if ! pg_isready &> /dev/null; then
    echo -e "  ${YELLOW}⚠ PostgreSQL 未运行${NC}"
    echo ""
    echo "请启动 PostgreSQL:"
    echo "  macOS:  brew services start postgresql@15"
    echo "  Linux:  sudo systemctl start postgresql"
    exit 1
fi
echo -e "  ✓ PostgreSQL 正在运行"

# Check Redis is running
if ! redis-cli ping &> /dev/null; then
    echo -e "  ${YELLOW}⚠ Redis 未运行${NC}"
    echo ""
    echo "请启动 Redis:"
    echo "  macOS:  brew services start redis"
    echo "  Linux:  sudo systemctl start redis"
    exit 1
fi
echo -e "  ✓ Redis 正在运行"

echo -e "${GREEN}环境检查通过！${NC}"
echo ""

# =================================
# 2. 创建配置文件
# =================================
echo -e "${YELLOW}[2/7] 创建配置文件...${NC}"

if [ ! -f ".env" ]; then
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "dev-secret-key-$(date +%s)")

    # Detect DB user for connection string
    if psql -U postgres -c "SELECT 1" &>/dev/null; then
        DB_USER="postgres"
    else
        DB_USER=$(whoami)
    fi

    cat > .env << EOF
# =================================
# Stock Analysis - 本地开发配置
# =================================

# Database (本地开发)
DATABASE_URL=postgresql://${DB_USER}@localhost:5432/stock_analysis

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
SECRET_KEY=${SECRET_KEY}
DEBUG=true

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600
EOF

    echo -e "  ✓ 已创建 .env 文件"
else
    echo -e "  - .env 文件已存在，跳过"
fi

echo ""

# =================================
# 3. 创建 Python 虚拟环境
# =================================
echo -e "${YELLOW}[3/7] 配置 Python 环境...${NC}"

cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo -e "  ✓ 虚拟环境创建完成"
else
    echo -e "  - 虚拟环境已存在"
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "  ✓ Python 依赖安装完成"
deactivate

cd "$PROJECT_DIR"
echo ""

# =================================
# 4. 安装前端依赖
# =================================
echo -e "${YELLOW}[4/7] 安装前端依赖...${NC}"

cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    npm install --silent
    echo -e "  ✓ 前端依赖安装完成"
else
    echo -e "  - node_modules 已存在，跳过"
fi

cd "$PROJECT_DIR"
echo ""

# =================================
# 5. 构建前端
# =================================
echo -e "${YELLOW}[5/7] 构建前端...${NC}"

cd "$PROJECT_DIR/frontend"

if [ ! -d "dist" ]; then
    npm run build --silent
    echo -e "  ✓ 前端构建完成"
else
    echo -e "  - dist 已存在，跳过 (如需重新构建请删除 frontend/dist)"
fi

cd "$PROJECT_DIR"
echo ""

# =================================
# 6. 初始化数据库
# =================================
echo -e "${YELLOW}[6/7] 初始化数据库...${NC}"

# Detect PostgreSQL user (macOS uses current user, Linux uses postgres)
if psql -U postgres -c "SELECT 1" &>/dev/null; then
    PG_USER="postgres"
else
    PG_USER=$(whoami)
fi
echo -e "  使用数据库用户: $PG_USER"

# Create database if not exists
DB_EXISTS=$(psql -U $PG_USER -tAc "SELECT 1 FROM pg_database WHERE datname='stock_analysis'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" != "1" ]; then
    createdb -U $PG_USER stock_analysis 2>/dev/null || true
    echo -e "  ✓ 数据库创建完成"
else
    echo -e "  - 数据库已存在"
fi

# Run init SQL
if [ -f "$PROJECT_DIR/docs/sql/init_tables.sql" ]; then
    psql -U $PG_USER -d stock_analysis -f "$PROJECT_DIR/docs/sql/init_tables.sql" -q 2>/dev/null || true
    echo -e "  ✓ 数据库表初始化完成"
fi

# Export for use in next step
export PG_USER

echo ""

# =================================
# 7. 创建默认管理员
# =================================
echo -e "${YELLOW}[7/7] 创建默认管理员...${NC}"

# Password hash for 'admin123'
ADMIN_HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4EnALGSq6D.9FKie'

psql -U $PG_USER -d stock_analysis -q << EOF
-- 创建管理员用户
INSERT INTO users (username, email, password_hash, status)
VALUES ('admin', 'admin@localhost', '${ADMIN_HASH}', 'active')
ON CONFLICT (username) DO NOTHING;

-- 创建管理员角色
INSERT INTO roles (name, description)
VALUES ('admin', '系统管理员')
ON CONFLICT (name) DO NOTHING;

-- 分配角色
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

-- 创建默认指标类型
INSERT INTO metric_types (code, name, description, file_pattern)
VALUES
    ('TTV', '总交易额', 'Total Trade Value', 'TTV'),
    ('EEE', '有效交易额', 'Effective Exchange', 'EEE')
ON CONFLICT (code) DO NOTHING;
EOF

echo -e "  ✓ 默认管理员创建完成"
echo ""

# =================================
# 完成
# =================================
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║            初始化完成！                    ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}默认管理员账户：${NC}"
echo "  用户名: admin"
echo "  密码:   admin123"
echo ""
echo -e "${YELLOW}⚠️  请在首次登录后立即修改密码！${NC}"
echo ""
echo -e "${BLUE}下一步：${NC}"
echo "  启动后端:   ./scripts/start.sh backend"
echo "  启动前端:   ./scripts/start.sh frontend"
echo "  启动全部:   ./scripts/start.sh all"
echo ""
