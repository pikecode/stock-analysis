#!/bin/bash
# ========================================
# 数据库备份脚本
# ========================================

set -e

# 配置变量
DB_NAME="stock_analysis"
DB_USER="stock_user"
DB_PASSWORD="stock_pass_2024"
BACKUP_DIR="/var/backups/stock-analysis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql"
KEEP_DAYS=30  # 保留最近30天的备份

echo "========================================="
echo "数据库备份"
echo "========================================="

# 创建备份目录
if [ ! -d "$BACKUP_DIR" ]; then
    echo "创建备份目录: $BACKUP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo chown $USER:$USER "$BACKUP_DIR"
fi

# 执行备份
echo "开始备份数据库: $DB_NAME"
echo "备份文件: $BACKUP_FILE"
echo ""

PGPASSWORD=$DB_PASSWORD pg_dump \
    -h localhost \
    -U $DB_USER \
    -d $DB_NAME \
    -F c \
    -b \
    -v \
    -f "$BACKUP_FILE.dump" \
    2>&1 | grep -v "^pg_dump:"

# 同时创建纯文本SQL备份（便于查看）
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h localhost \
    -U $DB_USER \
    -d $DB_NAME \
    -F p \
    > "$BACKUP_FILE"

# 压缩备份文件
echo ""
echo "压缩备份文件..."
gzip -f "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# 显示备份信息
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo ""
echo "========================================="
echo "备份完成！"
echo "========================================="
echo "备份文件: $BACKUP_FILE"
echo "备份大小: $BACKUP_SIZE"
echo "自定义格式: ${BACKUP_FILE%.gz}.dump"
echo ""

# 列出最近的备份
echo "最近的备份文件："
ls -lht "$BACKUP_DIR" | head -n 6

# 清理旧备份
echo ""
echo "========================================="
echo "清理旧备份 (保留最近 $KEEP_DAYS 天)"
echo "========================================="
find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$KEEP_DAYS -print -delete
find "$BACKUP_DIR" -name "backup_*.dump" -type f -mtime +$KEEP_DAYS -print -delete

# 统计备份信息
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

echo ""
echo "当前备份统计："
echo "  备份数量: $BACKUP_COUNT 个"
echo "  总占用空间: $TOTAL_SIZE"
echo ""

# 提供恢复命令提示
echo "========================================="
echo "恢复备份命令："
echo "========================================="
echo ""
echo "# 从自定义格式恢复 (推荐)"
echo "PGPASSWORD=$DB_PASSWORD pg_restore -h localhost -U $DB_USER -d $DB_NAME -c ${BACKUP_FILE%.gz}.dump"
echo ""
echo "# 从SQL文件恢复"
echo "gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
echo ""
echo "========================================="
