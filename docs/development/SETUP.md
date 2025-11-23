# 开发环境搭建

---

## 1. 环境要求

| 工具 | 版本 | 说明 |
|-----|------|------|
| Python | 3.11+ | 后端开发 |
| Node.js | 18+ | 前端开发 |
| PostgreSQL | 15+ | 数据库 |
| Redis | 7+ | 缓存 |
| Docker | 24+ | 容器化（可选） |

---

## 2. 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd stock-analysis

# 一键启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

**服务地址**:
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 前端: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 方式二：本地开发

#### 2.1 安装依赖

**macOS**:
```bash
# 安装Python
brew install python@3.11

# 安装PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 安装Redis
brew install redis
brew services start redis

# 安装Node.js
brew install node@18
```

**Ubuntu**:
```bash
# Python
sudo apt install python3.11 python3.11-venv

# PostgreSQL
sudo apt install postgresql-15

# Redis
sudo apt install redis-server

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

#### 2.2 创建数据库

```bash
# 创建数据库
createdb stock_analysis

# 初始化表结构
psql -d stock_analysis -f docs/sql/init_tables.sql
```

#### 2.3 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 编辑配置
vim .env
```

**.env 配置示例**:
```env
# 数据库
DATABASE_URL=postgresql://postgres:password@localhost:5432/stock_analysis

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 文件存储
UPLOAD_DIR=./uploads
```

**启动后端**:
```bash
# 开发模式（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用脚本
./scripts/dev.sh
```

#### 2.4 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 复制配置
cp .env.example .env.local

# 启动开发服务器
npm run dev
```

#### 2.5 启动Celery（异步任务）

```bash
# 新开终端
cd backend
source venv/bin/activate

# 启动Worker
celery -A tasks worker --loglevel=info

# 启动Beat（定时任务，可选）
celery -A tasks beat --loglevel=info
```

---

## 3. 项目结构

```
stock-analysis/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── auth.py
│   │   │   ├── stocks.py
│   │   │   ├── concepts.py
│   │   │   ├── rankings.py
│   │   │   ├── summaries.py
│   │   │   └── import.py
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   ├── repositories/   # 数据访问
│   │   └── utils/          # 工具函数
│   ├── tasks/              # Celery任务
│   ├── tests/              # 测试
│   ├── main.py             # 入口
│   └── requirements.txt
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/          # 页面
│   │   ├── components/     # 组件
│   │   ├── stores/         # Pinia状态
│   │   ├── api/            # API调用
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                   # 文档
│   ├── design/            # 设计文档
│   ├── development/       # 开发文档
│   ├── project/           # 项目管理
│   └── sql/               # SQL脚本
│
├── docker-compose.yml
└── README.md
```

---

## 4. 常用命令

### 后端

```bash
# 启动开发服务器
uvicorn main:app --reload

# 运行测试
pytest

# 运行测试（带覆盖率）
pytest --cov=app --cov-report=html

# 代码格式化
black app/
isort app/

# 代码检查
flake8 app/
mypy app/

# 数据库迁移
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### 前端

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 运行测试
npm run test
```

### Docker

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f [service]

# 重建镜像
docker-compose build --no-cache

# 进入容器
docker-compose exec backend bash
```

### 数据库

```bash
# 连接数据库
psql -d stock_analysis

# 初始化表
psql -d stock_analysis -f docs/sql/init_tables.sql

# 备份
pg_dump stock_analysis > backup.sql

# 恢复
psql stock_analysis < backup.sql
```

---

## 5. IDE配置

### VSCode

推荐插件:
- Python
- Pylance
- Vue - Official
- ESLint
- Prettier

**settings.json**:
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm

- 设置Python Interpreter为虚拟环境
- 启用Black格式化
- 配置isort

---

## 6. 常见问题

### Q: 数据库连接失败

```bash
# 检查PostgreSQL是否运行
brew services list  # macOS
systemctl status postgresql  # Linux

# 检查连接
psql -U postgres -h localhost
```

### Q: Redis连接失败

```bash
# 检查Redis是否运行
redis-cli ping
# 应返回 PONG
```

### Q: 前端API请求失败

1. 检查后端是否启动
2. 检查`.env.local`中的API地址
3. 检查CORS配置

### Q: Celery任务不执行

```bash
# 检查Celery Worker是否运行
celery -A tasks inspect active

# 检查Redis连接
redis-cli ping
```

---

## 7. 开发调试

### 后端调试

```python
# 使用print调试
print(f"DEBUG: {variable}")

# 使用logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable: {variable}")

# 使用pdb断点
import pdb; pdb.set_trace()
```

### 前端调试

```javascript
// 使用console
console.log('DEBUG:', variable)

// 使用Vue Devtools
// Chrome扩展：Vue.js devtools

// 使用debugger
debugger
```

### 数据库调试

```sql
-- 查看执行计划
EXPLAIN ANALYZE SELECT * FROM concept_stock_daily_rank WHERE stock_code = '600000';

-- 查看表大小
SELECT pg_size_pretty(pg_relation_size('concept_stock_daily_rank'));

-- 查看索引使用情况
SELECT * FROM pg_stat_user_indexes WHERE relname = 'concept_stock_daily_rank';
```
