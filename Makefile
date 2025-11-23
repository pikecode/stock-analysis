# =================================
# Stock Analysis - Makefile
# =================================

.PHONY: help init start stop status logs clean test build deploy

# Default target
help:
	@echo "Stock Analysis - 可用命令:"
	@echo ""
	@echo "本地开发:"
	@echo "  make init        - 首次初始化 (安装依赖、初始化数据库)"
	@echo "  make start       - 启动所有服务"
	@echo "  make stop        - 停止所有服务"
	@echo "  make status      - 查看服务状态"
	@echo "  make logs        - 查看日志"
	@echo ""
	@echo "单独启动:"
	@echo "  make backend     - 仅启动后端"
	@echo "  make frontend    - 仅启动前端"
	@echo "  make celery      - 仅启动 Celery"
	@echo ""
	@echo "构建:"
	@echo "  make build       - 构建前端"
	@echo "  make clean       - 清理构建文件"
	@echo ""
	@echo "数据库:"
	@echo "  make db-init     - 初始化数据库"
	@echo "  make db-shell    - 打开数据库命令行"
	@echo ""
	@echo "部署:"
	@echo "  make deploy      - 服务器部署 (需要 root)"

# =================================
# 本地开发
# =================================

init:
	./scripts/init.sh

start:
	./scripts/start.sh all

stop:
	./scripts/start.sh stop

status:
	./scripts/start.sh status

logs:
	./scripts/start.sh logs $(SERVICE)

# =================================
# 单独启动
# =================================

backend:
	./scripts/start.sh backend

frontend:
	./scripts/start.sh frontend

celery:
	./scripts/start.sh celery

# =================================
# 构建
# =================================

build:
	@echo "构建前端..."
	cd frontend && npm run build
	@echo "构建完成!"

clean:
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	rm -rf backend/venv
	rm -rf logs
	rm -rf .pids
	@echo "清理完成!"

# =================================
# 数据库
# =================================

db-init:
	./scripts/init-db.sh

db-shell:
	psql -U postgres -d stock_analysis

# =================================
# 部署
# =================================

deploy:
	@echo "服务器部署请使用:"
	@echo "  sudo ./deploy/native/deploy.sh install"

# =================================
# 开发工具
# =================================

# 安装依赖
install:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

# 运行测试
test:
	cd backend && source venv/bin/activate && pytest -v

# 代码检查
lint:
	cd backend && source venv/bin/activate && ruff check .
	cd frontend && npm run lint
