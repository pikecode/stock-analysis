# 部署文件说明

## 目录结构

```
deploy/
├── README.md                    # 本文件
├── docs/
│   └── DEPLOYMENT.md           # 详细部署文档
├── scripts/
│   ├── 00-deploy-all.sh        # 一键部署脚本（推荐）
│   ├── 01-init-database.sh     # 数据库初始化
│   ├── 02-deploy-backend.sh    # 后端部署
│   └── 03-deploy-frontend.sh   # 前端部署
└── configs/
    └── (预留用于配置文件模板)
```

## 快速开始

### 1. 准备服务器

确保服务器已安装：
- Ubuntu 20.04+
- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Nginx

### 2. 上传代码

```bash
# 在本地项目根目录执行
rsync -avz --exclude='node_modules' --exclude='venv' --exclude='.git' \
  ./ ubuntu@your-server-ip:/tmp/stock-analysis/
```

### 3. 执行部署

```bash
# SSH登录服务器
ssh ubuntu@your-server-ip

# 进入部署脚本目录
cd /tmp/stock-analysis/deploy/scripts

# 赋予执行权限
chmod +x *.sh

# 一键部署
./00-deploy-all.sh
```

## 脚本说明

### 00-deploy-all.sh
**一键部署脚本**，依次执行：
1. 初始化数据库
2. 部署后端服务
3. 部署前端服务

### 01-init-database.sh
**数据库初始化脚本**，完成：
- 创建PostgreSQL用户 `stock_user`
- 创建数据库 `stock_analysis`
- 执行SQL初始化脚本
- 配置数据库权限

**数据库信息：**
- 数据库名: `stock_analysis`
- 用户: `stock_user`
- 密码: `stock_pass_2024` (⚠️ 生产环境请修改)

### 02-deploy-backend.sh
**后端部署脚本**，完成：
- 复制后端代码到 `/var/www/stock-analysis/backend`
- 创建Python虚拟环境
- 安装依赖包 (FastAPI, SQLAlchemy等)
- 生成 `.env` 配置文件
- 创建systemd服务 `stock-analysis-backend`
- 启动后端服务（监听端口8000）

**服务管理：**
```bash
sudo systemctl status stock-analysis-backend
sudo systemctl restart stock-analysis-backend
sudo journalctl -u stock-analysis-backend -f
```

### 03-deploy-frontend.sh
**前端部署脚本**，完成：
- 复制前端代码到 `/var/www/stock-analysis/frontend`
- 安装npm依赖
- 执行生产构建 `npm run build`
- 配置Nginx反向代理
- 重启Nginx服务

**访问地址：**
- 前端: http://服务器IP
- API文档: http://服务器IP/api/docs

## 部署后配置

### 1. 修改数据库密码

```bash
# 登录PostgreSQL
sudo -u postgres psql

# 修改密码
ALTER USER stock_user WITH PASSWORD 'new_secure_password';

# 更新后端配置
sudo nano /var/www/stock-analysis/backend/.env
# 修改 DATABASE_URL 中的密码
```

### 2. 创建管理员账户

```bash
cd /var/www/stock-analysis/backend
source venv/bin/activate
python scripts/admin_setup.py
```

### 3. 配置域名和SSL

参见 `docs/DEPLOYMENT.md` 中的详细说明。

## 故障排查

### 后端服务无法启动
```bash
# 查看详细日志
sudo journalctl -u stock-analysis-backend -n 100

# 手动测试启动
cd /var/www/stock-analysis/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Nginx 502错误
```bash
# 检查后端是否运行
sudo systemctl status stock-analysis-backend

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/stock-analysis.error.log
```

### 数据库连接失败
```bash
# 测试数据库连接
psql -h localhost -U stock_user -d stock_analysis

# 检查PostgreSQL状态
sudo systemctl status postgresql
```

## 更新部署

### 更新代码
```bash
# 上传新代码
rsync -avz backend/ ubuntu@your-server:/var/www/stock-analysis/backend/
rsync -avz frontend/ ubuntu@your-server:/var/www/stock-analysis/frontend/

# 重启服务
ssh ubuntu@your-server
sudo systemctl restart stock-analysis-backend
cd /var/www/stock-analysis/frontend && npm run build
sudo systemctl reload nginx
```

## 详细文档

完整部署指南请查看: [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md)

内容包括：
- 服务器要求和软件安装
- 分步部署详解
- 安全配置建议
- 性能优化方案
- 监控和日志管理
- 常见问题解决
