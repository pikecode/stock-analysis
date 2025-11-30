#!/bin/bash
# ========================================
# 一键部署主脚本
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "股票分析系统 - 一键部署"
echo "========================================="
echo ""
echo "本脚本将按顺序执行："
echo "1. 数据库初始化"
echo "2. 后端服务部署"
echo "3. 前端服务部署"
echo ""
read -p "确认开始部署? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "部署已取消"
    exit 1
fi

# 1. 初始化数据库
echo ""
echo "========================================="
echo "步骤 1/3: 初始化数据库"
echo "========================================="
bash "$SCRIPT_DIR/01-init-database.sh"

# 2. 部署后端
echo ""
echo "========================================="
echo "步骤 2/3: 部署后端服务"
echo "========================================="
bash "$SCRIPT_DIR/02-deploy-backend.sh"

# 3. 部署前端
echo ""
echo "========================================="
echo "步骤 3/3: 部署前端服务"
echo "========================================="
bash "$SCRIPT_DIR/03-deploy-frontend.sh"

# 完成
echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "服务状态检查："
echo "----------------------------------------"
echo "后端服务："
sudo systemctl status stock-analysis-backend --no-pager | head -n 5
echo ""
echo "Nginx服务："
sudo systemctl status nginx --no-pager | head -n 5
echo ""
echo "========================================="
echo "访问地址: http://$(curl -s ifconfig.me)"
echo "API文档: http://$(curl -s ifconfig.me)/api/docs"
echo "========================================="
echo ""
echo "后续步骤："
echo "1. 修改后端 .env 文件中的 SECRET_KEY"
echo "2. 配置域名和SSL证书（可选）"
echo "3. 运行 python scripts/admin_setup.py 创建管理员账户"
echo "4. 导入初始数据"
echo "========================================="
