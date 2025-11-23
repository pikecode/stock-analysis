# Stock Analysis - 原生部署指南

本文档介绍如何在云服务器上直接部署 Stock Analysis（不使用 Docker）。

## 系统要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核+ |
| 内存 | 2 GB | 4 GB+ |
| 硬盘 | 20 GB | 50 GB+ |
| 系统 | Ubuntu 20.04+ | Ubuntu 22.04 |

### 支持的操作系统

- Ubuntu 20.04 / 22.04 ✅
- Debian 11 / 12 ✅
- CentOS 7 / 8 ✅
- Rocky Linux 8 / 9 ✅

## 快速部署

### 方式一：一键部署

```bash
# 1. 上传代码到服务器
scp -r stock-analysis root@your-server:/root/

# 2. SSH 登录服务器
ssh root@your-server

# 3. 进入部署目录
cd /root/stock-analysis/deploy/native

# 4. 安装系统依赖
sudo ./install-deps.sh

# 5. 部署应用
sudo ./deploy.sh install

# 6. 启动服务
sudo ./deploy.sh start
```

### 方式二：手动部署

详见下方 [手动部署步骤](#手动部署步骤)

## 部署后访问

| 服务 | 地址 |
|------|------|
| 网站 | http://服务器IP |
| API | http://服务器IP/api/v1 |
| 健康检查 | http://服务器IP/health |

### 默认账户

- 用户名: `admin`
- 密码: `admin123`

⚠️ **请在首次登录后立即修改密码！**

## 管理命令

```bash
# 查看状态
sudo ./deploy.sh status

# 启动服务
sudo ./deploy.sh start

# 停止服务
sudo ./deploy.sh stop

# 重启服务
sudo ./deploy.sh restart

# 查看日志
sudo ./deploy.sh logs api
sudo ./deploy.sh logs celery
sudo ./deploy.sh logs all

# 更新部署
sudo ./deploy.sh update
```

## 目录结构

部署后的目录结构：

```
/opt/stock-analysis/
├── backend/           # 后端代码
│   ├── venv/          # Python 虚拟环境
│   ├── app/           # 应用代码
│   └── tasks/         # Celery 任务
├── frontend/
│   └── dist/          # 前端构建文件
├── uploads/           # 上传文件目录
├── docs/              # 文档
└── .env               # 环境配置

/var/log/stock-analysis/
├── api.log            # API 日志
├── access.log         # 访问日志
├── celery.log         # Celery 日志
└── error.log          # 错误日志
```

## 配置文件

### 环境变量 `/opt/stock-analysis/.env`

```bash
# Database
DATABASE_URL=postgresql://stock_user:password@localhost:5432/stock_analysis

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Security
SECRET_KEY=your-secret-key
DEBUG=false
```

### Nginx 配置

```bash
# 配置文件位置
/etc/nginx/sites-available/stock-analysis

# 编辑配置
sudo nano /etc/nginx/sites-available/stock-analysis

# 测试并重载
sudo nginx -t && sudo systemctl reload nginx
```

## 手动部署步骤

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql redis-server nginx nodejs npm

# 启动服务
sudo systemctl enable postgresql redis-server nginx
sudo systemctl start postgresql redis-server nginx
```

### 2. 创建数据库

```bash
sudo -u postgres psql << EOF
CREATE USER stock_user WITH PASSWORD 'your_password';
CREATE DATABASE stock_analysis OWNER stock_user;
GRANT ALL PRIVILEGES ON DATABASE stock_analysis TO stock_user;
EOF
```

### 3. 部署后端

```bash
# 创建目录
sudo mkdir -p /opt/stock-analysis/backend
sudo cp -r backend/* /opt/stock-analysis/backend/

# 创建虚拟环境
cd /opt/stock-analysis/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

### 4. 部署前端

```bash
cd /opt/stock-analysis/frontend
npm install
npm run build
```

### 5. 配置 Systemd 服务

```bash
# 复制服务文件
sudo cp deploy/native/systemd/*.service /etc/systemd/system/

# 重载并启用
sudo systemctl daemon-reload
sudo systemctl enable stock-analysis-api stock-analysis-celery
sudo systemctl start stock-analysis-api stock-analysis-celery
```

### 6. 配置 Nginx

```bash
sudo cp deploy/native/nginx/stock-analysis.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/stock-analysis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## SSL 证书配置（可选）

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 常见问题

### Q: 服务启动失败？

```bash
# 查看详细日志
sudo journalctl -u stock-analysis-api -f

# 检查配置
cat /opt/stock-analysis/.env
```

### Q: 数据库连接失败？

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U stock_user -d stock_analysis
```

### Q: Nginx 502 错误？

```bash
# 检查后端是否运行
sudo systemctl status stock-analysis-api

# 检查端口
sudo netstat -tlnp | grep 8000
```

### Q: 如何备份数据？

```bash
# 备份数据库
pg_dump -U stock_user stock_analysis > backup.sql

# 恢复
psql -U stock_user stock_analysis < backup.sql
```

## 性能优化

### 1. 调整 Gunicorn Workers

编辑 `/etc/systemd/system/stock-analysis-api.service`:

```ini
# Workers = CPU核心数 * 2 + 1
ExecStart=... --workers 5 ...
```

### 2. 启用 PostgreSQL 连接池

```bash
sudo apt install pgbouncer
# 配置 /etc/pgbouncer/pgbouncer.ini
```

### 3. Redis 内存优化

```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 安全建议

1. **修改默认密码** - 首次登录后立即修改
2. **配置防火墙** - 只开放 80/443 端口
3. **启用 HTTPS** - 使用 Let's Encrypt
4. **定期备份** - 设置自动备份任务
5. **更新系统** - 定期更新系统和依赖

```bash
# 配置防火墙 (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```
