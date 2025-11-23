#!/bin/bash
# =================================
# Stock Analysis - 数据库初始化脚本
# =================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}初始化数据库...${NC}"

# Check PostgreSQL
if ! pg_isready &> /dev/null; then
    echo -e "${RED}PostgreSQL 未运行${NC}"
    echo "请先启动 PostgreSQL:"
    echo "  macOS:  brew services start postgresql@15"
    echo "  Linux:  sudo systemctl start postgresql"
    exit 1
fi

# Detect PostgreSQL user
if psql -U postgres -c "SELECT 1" &>/dev/null; then
    PG_USER="postgres"
else
    PG_USER=$(whoami)
fi
echo -e "  使用数据库用户: $PG_USER"

# Create database if not exists
DB_EXISTS=$(psql -U $PG_USER -tAc "SELECT 1 FROM pg_database WHERE datname='stock_analysis'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" != "1" ]; then
    echo "创建数据库..."
    createdb -U $PG_USER stock_analysis 2>/dev/null || true
    echo -e "  ✓ 数据库创建完成"
else
    echo -e "  - 数据库已存在"
fi

# Run init SQL
if [ -f "$PROJECT_DIR/docs/sql/init_tables.sql" ]; then
    echo "执行初始化 SQL..."
    psql -U $PG_USER -d stock_analysis -f "$PROJECT_DIR/docs/sql/init_tables.sql" -q 2>/dev/null || true
    echo -e "  ✓ 数据库表初始化完成"
fi

# Create admin user
echo "创建默认管理员..."
ADMIN_HASH='$2b$12$5WHoeRTXI2wUMqWVNP03MOcSsQXZ4aHAzc9XnnU0u3LvD1HDTTNVq'

psql -U $PG_USER -d stock_analysis -q << EOF
INSERT INTO users (username, email, password_hash, status)
VALUES ('admin', 'admin@example.com', '${ADMIN_HASH}', 'active')
ON CONFLICT (username) DO NOTHING;

INSERT INTO roles (name, display_name, description)
VALUES ('admin', '系统管理员', '系统管理员角色')
ON CONFLICT (name) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO metric_types (code, name, description, file_pattern)
VALUES
    ('TTV', '总交易额', 'Total Trade Value', 'TTV'),
    ('EEE', '有效交易额', 'Effective Exchange', 'EEE')
ON CONFLICT (code) DO NOTHING;
EOF

echo -e "${GREEN}数据库初始化完成！${NC}"
echo ""
echo "默认管理员账户:"
echo "  用户名: admin"
echo "  密码:   admin123"
echo ""
echo -e "${YELLOW}请在首次登录后立即修改密码！${NC}"
