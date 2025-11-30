# 股票分析系统部署指南

## 服务器要求

### 最低配置
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **CPU**: 2核
- **内存**: 4GB
- **磁盘**: 40GB

### 已验证环境
- **服务器**: 82.157.28.35
- **操作系统**: Ubuntu 20.04 LTS
- **用户**: ubuntu
- **内存**: 7.6GB
- **磁盘**: 99GB

## 预安装软件

部署脚本需要以下软件已安装：

- **Python 3.8+** ✅ (当前: 3.8.10)
- **Node.js 18+** ✅ (当前: v20.19.5)
- **PostgreSQL 12+** ✅ (当前: 12.22)
- **Nginx** ✅ (当前: 1.18.0)
- **Redis** ✅ (可选，用于Celery异步任务)

### 安装缺失软件（如需要）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装Nginx
sudo apt install nginx -y

# 安装Node.js (使用NodeSource仓库)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Python开发工具
sudo apt install python3 python3-pip python3-venv -y

# 安装Redis（可选）
sudo apt install redis-server -y
```

## 快速部署

### 1. 上传代码到服务器

```bash
# 在本地执行
cd /Users/peak/work/pikecode/stock-analysis
rsync -avz --exclude='node_modules' --exclude='venv' --exclude='.git' \
  ./ ubuntu@82.157.28.35:/tmp/stock-analysis/
```

### 2. 执行一键部署脚本

```bash
# SSH登录服务器
ssh ubuntu@82.157.28.35

# 进入项目目录
cd /tmp/stock-analysis/deploy/scripts

# 赋予执行权限
chmod +x *.sh

# 执行一键部署
./00-deploy-all.sh
```

脚本将自动完成：
- ✅ 创建数据库和用户
- ✅ 初始化数据库表结构
- ✅ 部署后端服务
- ✅ 构建前端项目
- ✅ 配置Nginx反向代理
- ✅ 创建systemd服务自动启动

## 分步部署（高级）

如果需要单独执行某个步骤，可以运行对应脚本：

### 步骤1: 初始化数据库
```bash
cd /tmp/stock-analysis/deploy/scripts
./01-init-database.sh
```

**功能：**
- 创建PostgreSQL用户 `stock_user`
- 创建数据库 `stock_analysis`
- 执行初始化SQL脚本 `backend/scripts/init-db-full.sql`

**数据库配置：**
- 数据库名: `stock_analysis`
- 用户名: `stock_user`
- 密码: `stock_pass_2024` (⚠️ 生产环境请修改)

### 步骤2: 部署后端
```bash
./02-deploy-backend.sh
```

**功能：**
- 复制代码到 `/var/www/stock-analysis/backend`
- 创建Python虚拟环境
- 安装依赖包
- 创建 `.env` 配置文件
- 注册systemd服务
- 启动后端服务（端口8000）

**后端配置文件位置：**
```
/var/www/stock-analysis/backend/.env
```

**systemd服务名称：**
```bash
sudo systemctl status stock-analysis-backend
sudo systemctl restart stock-analysis-backend
sudo systemctl stop stock-analysis-backend
```

### 步骤3: 部署前端
```bash
./03-deploy-frontend.sh
```

**功能：**
- 复制代码到 `/var/www/stock-analysis/frontend`
- 安装npm依赖
- 构建生产版本
- 配置Nginx
- 重启Nginx服务

**静态文件位置：**
```
/var/www/stock-analysis/frontend/dist
```

**Nginx配置文件：**
```
/etc/nginx/sites-available/stock-analysis
```

## 部署后配置

### 1. 修改安全配置

```bash
# 编辑后端配置文件
sudo nano /var/www/stock-analysis/backend/.env
```

**必须修改的配置：**
```env
# 生成新的密钥
SECRET_KEY=your-production-secret-key-$(openssl rand -hex 32)

# 生产环境配置
ENVIRONMENT=production
DEBUG=False
```

### 2. 创建管理员账户

```bash
cd /var/www/stock-analysis/backend
source venv/bin/activate
python scripts/admin_setup.py
```

按提示输入管理员用户名、邮箱和密码。

### 3. 配置域名（可选）

编辑Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/stock-analysis
```

修改 `server_name` 行：
```nginx
server_name your-domain.com www.your-domain.com;
```

重启Nginx：
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 配置SSL证书（推荐）

使用Let's Encrypt免费SSL证书：
```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 自动配置SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 5. 导入数据

```bash
# 登录系统后台
# 访问 http://your-server-ip/admin

# 使用管理员账户登录
# 进入 "数据导入" 页面
# 上传Excel数据文件
```

## 服务管理

### 后端服务

```bash
# 查看状态
sudo systemctl status stock-analysis-backend

# 启动服务
sudo systemctl start stock-analysis-backend

# 停止服务
sudo systemctl stop stock-analysis-backend

# 重启服务
sudo systemctl restart stock-analysis-backend

# 查看日志
sudo journalctl -u stock-analysis-backend -f

# 查看最近100行日志
sudo journalctl -u stock-analysis-backend -n 100
```

### Nginx服务

```bash
# 查看状态
sudo systemctl status nginx

# 重启Nginx
sudo systemctl restart nginx

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 测试配置文件
sudo nginx -t

# 查看访问日志
sudo tail -f /var/log/nginx/stock-analysis.access.log

# 查看错误日志
sudo tail -f /var/log/nginx/stock-analysis.error.log
```

### 数据库服务

```bash
# 查看PostgreSQL状态
sudo systemctl status postgresql

# 连接数据库
psql -h localhost -U stock_user -d stock_analysis

# 数据库备份
pg_dump -h localhost -U stock_user stock_analysis > backup_$(date +%Y%m%d).sql

# 数据库恢复
psql -h localhost -U stock_user -d stock_analysis < backup_20251130.sql
```

## 目录结构

```
/var/www/stock-analysis/
├── backend/
│   ├── app/                  # FastAPI应用代码
│   ├── venv/                 # Python虚拟环境
│   ├── .env                  # 环境配置文件
│   └── requirements.txt      # Python依赖
├── frontend/
│   ├── dist/                 # 构建后的静态文件
│   ├── src/                  # 源代码
│   └── package.json          # npm依赖
└── data/
    └── uploads/              # 上传文件目录
```

## 访问地址

- **前端页面**: http://服务器IP
- **API文档**: http://服务器IP/api/docs
- **管理后台**: http://服务器IP/admin

## 故障排查

### 问题1: 后端服务启动失败

```bash
# 查看详细日志
sudo journalctl -u stock-analysis-backend -n 200

# 检查端口占用
sudo netstat -tulpn | grep 8000

# 手动启动测试
cd /var/www/stock-analysis/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 问题2: Nginx 502 Bad Gateway

```bash
# 检查后端服务是否运行
sudo systemctl status stock-analysis-backend

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/stock-analysis.error.log
```

### 问题3: 数据库连接失败

```bash
# 检查PostgreSQL服务
sudo systemctl status postgresql

# 测试数据库连接
psql -h localhost -U stock_user -d stock_analysis

# 检查后端配置文件中的DATABASE_URL
cat /var/www/stock-analysis/backend/.env | grep DATABASE_URL
```

### 问题4: 前端页面无法访问

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查静态文件是否存在
ls -la /var/www/stock-analysis/frontend/dist/

# 重新构建前端
cd /var/www/stock-analysis/frontend
npm run build
```

## 更新部署

### 更新后端代码

```bash
# 在本地上传新代码
rsync -avz backend/ ubuntu@82.157.28.35:/var/www/stock-analysis/backend/

# 在服务器重启服务
ssh ubuntu@82.157.28.35
sudo systemctl restart stock-analysis-backend
```

### 更新前端代码

```bash
# 在本地上传并构建
rsync -avz frontend/ ubuntu@82.157.28.35:/var/www/stock-analysis/frontend/
ssh ubuntu@82.157.28.35 "cd /var/www/stock-analysis/frontend && npm run build && sudo systemctl reload nginx"
```

### 数据库迁移

如果有数据库结构变更：
```bash
# 备份当前数据库
pg_dump -h localhost -U stock_user stock_analysis > backup_before_migration.sql

# 执行迁移SQL
psql -h localhost -U stock_user -d stock_analysis -f migration.sql

# 重启后端服务
sudo systemctl restart stock-analysis-backend
```

## 性能优化

### 1. 数据库优化

```sql
-- 创建常用查询索引
CREATE INDEX IF NOT EXISTS idx_concept_stock_daily_rank_date
ON concept_stock_daily_rank(trade_date, metric_code);

CREATE INDEX IF NOT EXISTS idx_concept_daily_summary_date
ON concept_daily_summary(trade_date, concept_id, metric_code);

-- 定期清理和优化
VACUUM ANALYZE;
```

### 2. Nginx缓存配置

在Nginx配置中添加：
```nginx
# 缓存路径
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

# API缓存（仅针对GET请求）
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$request_uri";
    proxy_cache_bypass $http_cache_control;
    # ... 其他配置
}
```

### 3. 后端性能调优

编辑systemd服务配置：
```bash
sudo nano /etc/systemd/system/stock-analysis-backend.service
```

增加workers数量：
```ini
ExecStart=/var/www/stock-analysis/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
```

重启服务：
```bash
sudo systemctl daemon-reload
sudo systemctl restart stock-analysis-backend
```

## 监控和日志

### 设置日志轮转

```bash
# 创建日志轮转配置
sudo nano /etc/logrotate.d/stock-analysis
```

添加内容：
```
/var/log/nginx/stock-analysis.*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 监控脚本

创建简单的健康检查脚本：
```bash
#!/bin/bash
# /usr/local/bin/stock-analysis-health-check.sh

# 检查后端服务
if ! systemctl is-active --quiet stock-analysis-backend; then
    echo "后端服务异常，尝试重启..."
    systemctl restart stock-analysis-backend
fi

# 检查Nginx
if ! systemctl is-active --quiet nginx; then
    echo "Nginx服务异常，尝试重启..."
    systemctl restart nginx
fi

# 检查API响应
if ! curl -f http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1; then
    echo "API健康检查失败"
fi
```

设置定时任务：
```bash
# 编辑crontab
sudo crontab -e

# 每5分钟检查一次
*/5 * * * * /usr/local/bin/stock-analysis-health-check.sh
```

## 安全建议

1. **修改默认密码**:
   - 数据库密码
   - 管理员账户密码
   - SECRET_KEY

2. **配置防火墙**:
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

3. **限制PostgreSQL访问**:
编辑 `/etc/postgresql/12/main/pg_hba.conf`，确保只允许本地连接。

4. **定期备份数据库**:
设置自动备份cron任务。

5. **启用HTTPS**:
使用Let's Encrypt配置SSL证书。

## 支持

如有问题，请检查：
- 后端日志: `sudo journalctl -u stock-analysis-backend -f`
- Nginx日志: `/var/log/nginx/stock-analysis.error.log`
- 数据库日志: `/var/log/postgresql/postgresql-12-main.log`
