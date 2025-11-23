# 快速开始指南

本文档提供快速启动开发的步骤说明。

---

## 📋 前置条件

### 开发环境要求

| 软件 | 版本要求 | 安装检查 |
|------|---------|---------|
| **Python** | 3.11+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **Docker** | 24+ | `docker --version` |
| **Docker Compose** | 2.20+ | `docker-compose --version` |
| **PostgreSQL** | 15+ | `psql --version` (可选，推荐Docker) |
| **Redis** | 7+ | `redis-cli --version` (可选，推荐Docker) |
| **Git** | 2.0+ | `git --version` |

### 快速安装开发环境

**macOS**:
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python@3.11 node docker git

# 启动Docker Desktop
open -a Docker
```

**Ubuntu/Debian**:
```bash
# 更新包管理器
sudo apt update

# 安装Python
sudo apt install python3.11 python3.11-venv python3-pip

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Windows**:
- 安装 [Python 3.11](https://www.python.org/downloads/)
- 安装 [Node.js 18](https://nodejs.org/)
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 安装 [Git](https://git-scm.com/download/win)

---

## 🚀 快速启动（开发模式）

### 方式一：Docker Compose 一键启动 (推荐)

**1. 克隆项目**
```bash
git clone <repository-url>
cd stock-analysis
```

**2. 配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

**3. 启动所有服务**
```bash
docker-compose up -d
```

**4. 初始化数据库**
```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 初始化默认数据
docker-compose exec backend python scripts/init_data.py
```

**5. 访问系统**
- 后台管理: http://localhost:8080
- 用户展示: http://localhost:8081
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001

**默认登录信息**:
- 用户名: `admin`
- 密码: `admin123`

---

### 方式二：本地开发（调试模式）

#### 后端开发

**1. 启动依赖服务**
```bash
# 只启动PostgreSQL、Redis、MinIO
docker-compose up -d postgres redis minio
```

**2. 创建虚拟环境**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. 安装依赖**
```bash
pip install -r requirements.txt
```

**4. 配置环境变量**
```bash
# backend/.env
DATABASE_URL=postgresql://stockuser:password@localhost:5432/stock_analysis
REDIS_URL=redis://:password@localhost:6379/0
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
SECRET_KEY=your-secret-key-here-min-32-chars
```

**5. 初始化数据库**
```bash
# 创建数据库表
alembic upgrade head

# 初始化数据
python scripts/init_data.py
```

**6. 启动开发服务器**
```bash
# 启动API服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 新开终端，启动Celery Worker
celery -A app.tasks worker --loglevel=info
```

**7. 访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

#### 前端开发

**后台管理前端**:
```bash
cd admin-frontend

# 安装依赖
npm install

# 配置API地址
cp .env.example .env.local
# 编辑 .env.local
# VITE_API_BASE_URL=http://localhost:8000

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

**用户展示前端**:
```bash
cd user-frontend

# 安装依赖
npm install

# 配置API地址
cp .env.example .env.local

# 启动开发服务器
npm run dev

# 访问 http://localhost:5174
```

---

## 📂 项目结构

```
stock-analysis/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── tasks/          # 异步任务
│   ├── alembic/            # 数据库迁移
│   ├── scripts/            # 脚本工具
│   ├── tests/              # 测试
│   ├── requirements.txt    # Python依赖
│   └── main.py            # 入口文件
│
├── admin-frontend/         # 后台管理前端
│   ├── src/
│   │   ├── views/         # 页面
│   │   ├── components/    # 组件
│   │   ├── api/           # API封装
│   │   └── router/        # 路由
│   └── package.json
│
├── user-frontend/          # 用户展示前端
│   └── (同上)
│
├── deployment/             # 部署配置
│   ├── docker-compose.yml
│   ├── nginx/
│   └── scripts/
│
├── docs/                   # 文档
│   ├── DESIGN.md          # 设计文档
│   ├── DESIGN_REVIEW.md   # 设计评审
│   ├── API.md             # API文档
│   └── DEPLOYMENT.md      # 部署文档
│
├── .env.example            # 环境变量示例
└── README.md              # 项目说明
```

---

## 🔧 常用开发命令

### 后端

```bash
# 数据库迁移
alembic revision --autogenerate -m "description"  # 生成迁移文件
alembic upgrade head                              # 应用迁移
alembic downgrade -1                              # 回滚一个版本

# 测试
pytest                                            # 运行所有测试
pytest tests/test_stock.py                        # 运行单个测试文件
pytest --cov=app                                  # 测试覆盖率

# 代码检查
black .                                           # 代码格式化
flake8 app/                                       # 代码检查
mypy app/                                         # 类型检查

# 启动服务
uvicorn main:app --reload                         # 开发服务器
uvicorn main:app --host 0.0.0.0 --port 8000      # 生产服务器
celery -A app.tasks worker -l info               # Celery Worker
celery -A app.tasks beat -l info                 # Celery Beat
```

### 前端

```bash
# 开发
npm run dev                                       # 启动开发服务器
npm run build                                     # 构建生产版本
npm run preview                                   # 预览生产版本

# 代码检查
npm run lint                                      # ESLint检查
npm run lint:fix                                  # 自动修复
npm run type-check                                # TypeScript类型检查

# 测试
npm run test                                      # 运行测试
npm run test:coverage                             # 测试覆盖率
```

### Docker

```bash
# 启动服务
docker-compose up -d                              # 后台启动
docker-compose up -d backend                      # 启动单个服务

# 查看日志
docker-compose logs -f                            # 所有服务日志
docker-compose logs -f backend                    # 单个服务日志

# 停止服务
docker-compose stop                               # 停止服务
docker-compose down                               # 停止并删除容器
docker-compose down -v                            # 同时删除数据卷

# 重启服务
docker-compose restart backend                    # 重启单个服务
docker-compose up -d --build                      # 重新构建并启动

# 进入容器
docker-compose exec backend bash                  # 进入后端容器
docker-compose exec postgres psql -U stockuser   # 进入数据库

# 清理
docker-compose down -v --rmi all                 # 删除所有（容器、卷、镜像）
```

---

## 🗄️ 数据库管理

### 连接数据库

```bash
# 通过Docker
docker-compose exec postgres psql -U stockuser -d stock_analysis

# 本地连接
psql -h localhost -U stockuser -d stock_analysis
```

### 常用SQL命令

```sql
-- 查看所有表
\dt

-- 查看表结构
\d users
\d stock_daily_data

-- 查看数据
SELECT * FROM users LIMIT 10;
SELECT * FROM concepts;

-- 查看分区
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 查看索引
\di

-- 查看统计信息
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 数据导入测试

```bash
# 使用提供的测试数据
docker-compose exec backend python scripts/import_test_data.py \
    --concept-file /data/2025-08-22-01-31.csv \
    --daily-file /data/EEE.txt
```

---

## 🧪 测试

### 运行测试

```bash
# 后端测试
cd backend
pytest -v                                         # 详细模式
pytest --cov=app --cov-report=html               # 生成HTML覆盖率报告
pytest -k test_stock                             # 运行特定测试

# 前端测试
cd admin-frontend
npm run test                                      # 单元测试
npm run test:e2e                                  # E2E测试
```

### 测试数据准备

```python
# backend/tests/conftest.py
import pytest
from app.core.database import get_db

@pytest.fixture
def test_db():
    """测试数据库fixture"""
    db = next(get_db())
    yield db
    db.rollback()

@pytest.fixture
def test_user(test_db):
    """创建测试用户"""
    user = User(username="testuser", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    return user
```

---

## 📊 监控与调试

### 查看日志

```bash
# 应用日志
docker-compose logs -f backend

# 数据库日志
docker-compose logs -f postgres

# 实时日志
tail -f logs/app.log
```

### 性能分析

```bash
# API性能测试
ab -n 1000 -c 10 http://localhost:8000/api/v1/stocks

# 数据库慢查询
docker-compose exec postgres psql -U stockuser -c "
    SELECT query, calls, total_time, mean_time
    FROM pg_stat_statements
    ORDER BY mean_time DESC
    LIMIT 10;
"
```

### Redis调试

```bash
# 连接Redis
docker-compose exec redis redis-cli -a password

# 查看所有键
KEYS *

# 查看缓存
GET stock:600000
GET concept:1:ranks:2025-08-21

# 清空缓存
FLUSHALL
```

---

## 🐛 常见问题

### 1. 数据库连接失败

**问题**: `could not connect to server`

**解决**:
```bash
# 检查PostgreSQL是否启动
docker-compose ps postgres

# 查看日志
docker-compose logs postgres

# 重启服务
docker-compose restart postgres
```

### 2. 端口被占用

**问题**: `port is already allocated`

**解决**:
```bash
# 查看端口占用
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或修改docker-compose.yml中的端口映射
```

### 3. 依赖安装失败

**问题**: `pip install` 失败

**解决**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 清理缓存
pip cache purge
```

### 4. 前端热更新不生效

**问题**: 修改代码后页面不更新

**解决**:
```bash
# 删除node_modules重新安装
rm -rf node_modules
npm install

# 清理缓存
rm -rf .vite
npm run dev
```

### 5. Alembic迁移冲突

**问题**: `multiple heads detected`

**解决**:
```bash
# 查看当前版本
alembic current

# 合并分支
alembic merge heads

# 或删除冲突的迁移文件，重新生成
```

---

## 📖 下一步

1. **阅读设计文档**: [docs/DESIGN.md](./DESIGN.md)
2. **阅读评审文档**: [docs/DESIGN_REVIEW.md](./DESIGN_REVIEW.md)
3. **开始第一个功能**: 按照开发计划的Phase 1开始
4. **提交第一个PR**: 完成后提交Pull Request

---

## 💡 开发建议

1. **使用Git分支**: 每个功能创建单独分支
   ```bash
   git checkout -b feature/user-auth
   git checkout -b feature/data-import
   ```

2. **提交规范**: 使用Conventional Commits
   ```bash
   git commit -m "feat: add user authentication"
   git commit -m "fix: resolve database connection issue"
   git commit -m "docs: update API documentation"
   ```

3. **代码审查**: 提交前自我审查
   - 运行测试: `pytest` / `npm test`
   - 代码格式: `black .` / `npm run lint`
   - 类���检查: `mypy app/`

4. **保持更新**: 定期拉取最新代码
   ```bash
   git pull origin main
   ```

---

## 🆘 获取帮助

- **文档**: 查看 `docs/` 目录下的文档
- **API文档**: http://localhost:8000/docs
- **问题追踪**: GitHub Issues
- **代码示例**: 查看 `tests/` 目录

---

**Happy Coding! 🚀**
