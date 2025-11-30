#!/bin/bash
# ========================================
# 数据库初始化脚本
# ========================================

set -e  # 遇到错误立即退出

# 配置变量
DB_NAME="stock_analysis"
DB_USER="stock_user"
DB_PASSWORD="stock_pass_2024"
POSTGRES_USER="postgres"

echo "========================================="
echo "开始初始化数据库..."
echo "========================================="

# 1. 创建数据库用户（如果不存在）
echo "步骤 1/4: 创建数据库用户..."
sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# 2. 创建数据库（如果不存在）
echo "步骤 2/4: 创建数据库..."
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME || \
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING 'UTF8';"

# 3. 赋予权限
echo "步骤 3/4: 配置数据库权限..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 4. 执行数据库结构初始化SQL
echo "步骤 4/4: 初始化数据库结构..."
PSQL_COMMAND="PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"

# 检查SQL文件是否存在
SQL_FILE="../backend/scripts/init-db-full.sql"
if [ ! -f "$SQL_FILE" ]; then
    echo "错误: 找不到SQL文件 $SQL_FILE"
    exit 1
fi

# 执行SQL初始化
$PSQL_COMMAND -f "$SQL_FILE"

echo "========================================="
echo "数据库初始化完成！"
echo "========================================="
echo "数据库名称: $DB_NAME"
echo "数据库用户: $DB_USER"
echo "数据库密码: $DB_PASSWORD"
echo "========================================="
