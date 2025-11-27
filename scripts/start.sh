#!/bin/bash
# =================================
# Stock Analysis - 本地启动脚本
# =================================
# 用法:
#   ./scripts/start.sh backend   - 启动后端
#   ./scripts/start.sh frontend  - 启动前端开发服务器
#   ./scripts/start.sh celery    - 启动 Celery Worker
#   ./scripts/start.sh all       - 启动全部服务
#   ./scripts/start.sh stop      - 停止所有服务

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# PID files
PID_DIR="$PROJECT_DIR/.pids"
mkdir -p "$PID_DIR"

cd "$PROJECT_DIR"

# =================================
# Helper Functions
# =================================

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════╗"
    echo "║       Stock Analysis - 本地开发            ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo -e "${CYAN}用法:${NC}"
    echo "  $0 <command>"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo "  backend    启动后端 API 服务"
    echo "  frontend   启动前端开发服务器"
    echo "  celery     启动 Celery Worker"
    echo "  all        启动全部服务"
    echo "  stop       停止所有服务"
    echo "  status     查看服务状态"
    echo "  logs       查看后端日志"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 all      # 启动全部"
    echo "  $0 backend  # 仅启动后端"
    echo "  $0 stop     # 停止所有"
}

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port in use
    else
        return 1  # Port free
    fi
}

# 健康检查：验证服务是否真正启动
health_check_backend() {
    local max_attempts=20
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:8000/health 2>/dev/null | grep -q "healthy"; then
            return 0  # Service is healthy
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1  # Service not responding
}

health_check_frontend() {
    local max_attempts=20
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:3000 >/dev/null 2>&1; then
            return 0  # Service is responding
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1  # Service not responding
}

kill_by_pid_file() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null || true
            sleep 1
            kill -9 $pid 2>/dev/null || true
        fi
        rm -f "$pid_file"
    fi
}

# =================================
# Start Backend
# =================================

start_backend() {
    echo -e "${YELLOW}启动后端 API...${NC}"

    # Force kill if port is already in use
    if check_port 8000; then
        echo -e "  ${YELLOW}⚠️  端口 8000 已被占用，尝试清理...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    cd "$PROJECT_DIR/backend"
    source venv/bin/activate

    # Load environment
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

    # Start uvicorn in background
    nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload \
        > "$PROJECT_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"

    deactivate
    cd "$PROJECT_DIR"

    echo -e "  ${CYAN}⏳ 等待后端服务启动...${NC}"
    if health_check_backend; then
        echo -e "  ${GREEN}✓ 后端已启动: http://127.0.0.1:8000${NC}"
        echo -e "  ${GREEN}✓ API 文档 (Swagger): http://127.0.0.1:8000/docs${NC}"
        echo -e "  ${GREEN}✓ API 文档 (ReDoc): http://127.0.0.1:8000/redoc${NC}"
        echo -e "  ${GREEN}✓ 进程 PID: $BACKEND_PID${NC}"
    else
        echo -e "  ${RED}✗ 后端启动失败${NC}"
        echo -e "  ${YELLOW}最近的日志:${NC}"
        tail -20 "$PROJECT_DIR/logs/backend.log" | sed 's/^/    /'
        return 1
    fi
}

# =================================
# Start Frontend
# =================================

start_frontend() {
    echo -e "${YELLOW}启动前端开发服务器...${NC}"

    # Force kill if port is already in use
    if check_port 3000; then
        echo -e "  ${YELLOW}⚠️  端口 3000 已被占用，尝试清理...${NC}"
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    cd "$PROJECT_DIR/frontend"

    # Start vite in background
    nohup npm run dev > "$PROJECT_DIR/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"

    cd "$PROJECT_DIR"

    echo -e "  ${CYAN}⏳ 等待前端服务启动...${NC}"
    if health_check_frontend; then
        echo -e "  ${GREEN}✓ 前端已启动: http://127.0.0.1:3000${NC}"
        echo -e "  ${GREEN}✓ 进程 PID: $FRONTEND_PID${NC}"
    else
        echo -e "  ${RED}✗ 前端启动失败${NC}"
        echo -e "  ${YELLOW}最近的日志:${NC}"
        tail -20 "$PROJECT_DIR/logs/frontend.log" | sed 's/^/    /'
        return 1
    fi
}

# =================================
# Start Celery
# =================================

start_celery() {
    echo -e "${YELLOW}启动 Celery Worker...${NC}"

    kill_by_pid_file "$PID_DIR/celery.pid"

    cd "$PROJECT_DIR/backend"
    source venv/bin/activate

    # Load environment
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

    # Start celery in background
    nohup celery -A tasks.celery_app worker --loglevel=info \
        > "$PROJECT_DIR/logs/celery.log" 2>&1 &
    echo $! > "$PID_DIR/celery.pid"

    deactivate
    cd "$PROJECT_DIR"

    sleep 2
    echo -e "  ${GREEN}✓ Celery Worker 已启动${NC}"
}

# =================================
# Stop All
# =================================

stop_all() {
    echo -e "${YELLOW}停止所有服务...${NC}"

    kill_by_pid_file "$PID_DIR/backend.pid"
    echo -e "  ✓ 后端已停止"

    kill_by_pid_file "$PID_DIR/frontend.pid"
    echo -e "  ✓ 前端已停止"

    kill_by_pid_file "$PID_DIR/celery.pid"
    echo -e "  ✓ Celery 已停止"

    # Force kill any remaining processes on our ports
    echo -e "${CYAN}清理残留进程...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    lsof -ti:3002 | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}所有服务已停止${NC}"
}

# =================================
# Status
# =================================

show_status() {
    print_header
    echo -e "${CYAN}服务状态:${NC}"
    echo ""

    if check_port 8000; then
        echo -e "  ${GREEN}● 后端 API${NC}     http://localhost:8000"
    else
        echo -e "  ${RED}○ 后端 API${NC}     未运行"
    fi

    if check_port 3000; then
        echo -e "  ${GREEN}● 前端开发${NC}     http://localhost:3000"
    else
        echo -e "  ${RED}○ 前端开发${NC}     未运行"
    fi

    if [ -f "$PID_DIR/celery.pid" ] && kill -0 $(cat "$PID_DIR/celery.pid") 2>/dev/null; then
        echo -e "  ${GREEN}● Celery${NC}       运行中"
    else
        echo -e "  ${RED}○ Celery${NC}       未运行"
    fi

    # Check database
    if pg_isready &>/dev/null; then
        echo -e "  ${GREEN}● PostgreSQL${NC}   运行中"
    else
        echo -e "  ${RED}○ PostgreSQL${NC}   未运行"
    fi

    # Check Redis
    if redis-cli ping &>/dev/null; then
        echo -e "  ${GREEN}● Redis${NC}        运行中"
    else
        echo -e "  ${RED}○ Redis${NC}        未运行"
    fi

    echo ""
}

# =================================
# Logs
# =================================

show_logs() {
    local service=${1:-backend}
    local log_file="$PROJECT_DIR/logs/${service}.log"

    if [ -f "$log_file" ]; then
        tail -f "$log_file"
    else
        echo -e "${RED}日志文件不存在: $log_file${NC}"
    fi
}

# =================================
# Start All
# =================================

start_all() {
    print_header

    # Create logs directory
    mkdir -p "$PROJECT_DIR/logs"

    # Check prerequisites
    if ! pg_isready &>/dev/null; then
        echo -e "${RED}❌ PostgreSQL 未运行，请先启动数据库${NC}"
        echo -e "${CYAN}提示: brew services start postgresql${NC}"
        exit 1
    fi

    if ! redis-cli ping &>/dev/null; then
        echo -e "${RED}❌ Redis 未运行，请先启动 Redis${NC}"
        echo -e "${CYAN}提示: brew services start redis${NC}"
        exit 1
    fi

    echo -e "${CYAN}✓ 依赖检查完成${NC}"
    echo ""
    echo -e "${YELLOW}启动所有服务...${NC}"
    echo ""

    start_backend || exit 1
    start_celery
    start_frontend || exit 1

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 所有服务已启动！${NC}"
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}📱 访问地址:${NC}"
    echo -e "  前端:         ${BLUE}http://127.0.0.1:3000${NC}"
    echo -e "  API:          ${BLUE}http://127.0.0.1:8000${NC}"
    echo -e "  文档 (Swagger): ${BLUE}http://127.0.0.1:8000/docs${NC}"
    echo -e "  文档 (ReDoc):   ${BLUE}http://127.0.0.1:8000/redoc${NC}"
    echo ""
    echo -e "${CYAN}👤 默认账户:${NC}"
    echo "  Admin 用户:"
    echo "    用户名: admin"
    echo "    密码:   admin"
    echo "  Customer 用户:"
    echo "    用户名: customer"
    echo "    密码:   customer"
    echo "  Test 用户:"
    echo "    用户名: testuser"
    echo "    密码:   123456"
    echo ""
    echo -e "${YELLOW}⏹️  停止服务: ./scripts/start.sh stop${NC}"
    echo -e "${YELLOW}📋 查看状态: ./scripts/start.sh status${NC}"
    echo -e "${YELLOW}📝 查看日志: ./scripts/start.sh logs backend${NC}"
    echo ""
    echo -e "${CYAN}💡 提示:${NC}"
    echo "  如果登录按钮无反应，请在浏览器开发者工具清除 localStorage:"
    echo "  浏览器 DevTools (F12) → Application → LocalStorage → 删除旧 token"
    echo ""
}

# =================================
# Main
# =================================

case "${1:-}" in
    backend)
        print_header
        mkdir -p "$PROJECT_DIR/logs"
        start_backend
        ;;
    frontend)
        print_header
        mkdir -p "$PROJECT_DIR/logs"
        start_frontend
        ;;
    celery)
        print_header
        mkdir -p "$PROJECT_DIR/logs"
        start_celery
        ;;
    all)
        start_all
        ;;
    stop)
        print_header
        stop_all
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    -h|--help|help)
        print_header
        print_usage
        ;;
    *)
        print_header
        print_usage
        exit 1
        ;;
esac
