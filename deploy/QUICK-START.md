# 快速部署与更新指南

## 📋 目录

- [首次部署](#首次部署)
- [代码更新](#代码更新)
- [常用操作](#常用操作)
- [故障排查](#故障排查)

---

## 首次部署

### 前提条件

服务器需要已安装：
- Ubuntu 20.04+
- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Nginx
- sshpass (本地需要)

### 部署步骤

```bash
# 1. 进入部署脚本目录
cd deploy/scripts

# 2. 执行一键部署
./00-deploy-all.sh

# 或者分步部署
./01-init-database.sh    # 初始化数据库
./02-deploy-backend.sh   # 部署后端
./03-deploy-frontend.sh  # 部署前端
```

### 部署后配置

```bash
# SSH登录服务器
ssh ubuntu@82.157.28.35

# 1. 创建管理员账户
cd /var/www/stock-analysis/backend
source venv/bin/activate
python scripts/admin_setup.py

# 2. 修改生产环境配置（可选）
sudo nano /var/www/stock-analysis/backend/.env
# 修改SECRET_KEY和数据库密码

# 3. 导入数据
# 访问 https://qwquant.com/admin 登录后台导入数据
```

---

## 代码更新

### 方式一：完整更新（推荐）

当后端和前端都有更新时使用：

```bash
cd deploy/scripts
./update-production.sh
```

**执行内容：**
- ✅ 自动备份数据库
- ✅ 备份当前代码
- ✅ 上传并更新后端代码
- ✅ 更新Python依赖
- ✅ 重启后端服务
- ✅ 上传并构建前端
- ✅ 重启Nginx
- ✅ 验证部署结果

**预计耗时：** 2-3分钟

### 方式二：仅更新后端

当只修改了后端代码时：

```bash
cd deploy/scripts
./update-backend.sh
```

**执行内容：**
- ✅ 备份数据库
- ✅ 上传后端代码
- ✅ 更新Python依赖
- ✅ 重启后端服务

**预计耗时：** 30-60秒

### 方式三：仅更新前端

当只修改了前端代码时：

```bash
cd deploy/scripts
./update-frontend.sh
```

**执行内容：**
- ✅ 备份当前前端
- ✅ 上传前端代码
- ✅ 构建生产版本
- ✅ 重启Nginx

**预计耗时：** 30-60秒

---

## 常用操作

### 查看服务状态

```bash
ssh ubuntu@82.157.28.35

# 后端服务状态
sudo systemctl status stock-analysis-backend

# Nginx状态
sudo systemctl status nginx

# PostgreSQL状态
sudo systemctl status postgresql
```

### 查看日志

```bash
# 后端日志（实时）
sudo journalctl -u stock-analysis-backend -f

# 后端日志（最近100行）
sudo journalctl -u stock-analysis-backend -n 100

# Nginx访问日志
sudo tail -f /var/log/nginx/qwquant_access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/qwquant_error.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart stock-analysis-backend

# 重启Nginx
sudo systemctl reload nginx

# 重启PostgreSQL
sudo systemctl restart postgresql
```

### 数据库备份

```bash
# 手动备份
cd /var/www/stock-analysis/backend
PGPASSWORD=stock_pass_2024 pg_dump -h localhost -U stock_user stock_analysis > backup_$(date +%Y%m%d_%H%M%S).sql
gzip backup_*.sql

# 使用备份脚本
cd /var/www/stock-analysis/backend
../deploy/scripts/backup-database.sh
```

### 数据库恢复

```bash
# 恢复备份
cd /var/www/stock-analysis/backend
gunzip -c backups/backup_20251130_150000.sql.gz | PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis
```

---

## 故障排查

### 问题1: 后端服务无法启动

**症状：** `systemctl status stock-analysis-backend` 显示failed

**排查步骤：**

```bash
# 1. 查看详细错误日志
sudo journalctl -u stock-analysis-backend -n 100

# 2. 检查端口占用
sudo netstat -tuln | grep 8000

# 3. 手动启动测试
cd /var/www/stock-analysis/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 4. 检查数据库连接
psql -h localhost -U stock_user -d stock_analysis
```

**常见原因：**
- Python依赖缺失 → `pip install -r requirements.txt`
- 数据库连接失败 → 检查 `.env` 中的 `DATABASE_URL`
- 端口被占用 → `sudo lsof -i :8000` 查找占用进程

### 问题2: 前端页面502错误

**症状：** 访问 https://qwquant.com 显示502 Bad Gateway

**排查步骤：**

```bash
# 1. 检查后端服务
sudo systemctl status stock-analysis-backend

# 2. 检查Nginx配置
sudo nginx -t

# 3. 查看Nginx错误日志
sudo tail -50 /var/log/nginx/qwquant_error.log

# 4. 测试后端端口
curl http://127.0.0.1:8000/api/v1/stocks?page=1&page_size=1
```

**解决方法：**
```bash
# 重启后端服务
sudo systemctl restart stock-analysis-backend

# 重启Nginx
sudo systemctl reload nginx
```

### 问题3: 前端页面空白

**症状：** 页面加载但显示空白

**排查步骤：**

```bash
# 1. 检查dist目录
ls -la /var/www/stock-analysis/frontend/dist/

# 2. 检查Nginx配置
sudo cat /etc/nginx/sites-enabled/stock-analysis-domain

# 3. 查看浏览器控制台错误
# F12打开开发者工具查看Console和Network标签
```

**解决方法：**
```bash
# 重新构建前端
cd /var/www/stock-analysis/frontend
npm run build
sudo systemctl reload nginx
```

### 问题4: API返回404

**症状：** 访问 `/api/v1/*` 返回404

**排查步骤：**

```bash
# 1. 检查后端路由
curl http://127.0.0.1:8000/api/v1/stocks

# 2. 查看Nginx代理配置
sudo cat /etc/nginx/sites-enabled/stock-analysis-domain | grep -A 10 "location /api/"

# 3. 检查后端日志
sudo journalctl -u stock-analysis-backend -n 50
```

### 问题5: 数据库连接失败

**症状：** 后端日志显示数据库连接错误

**排查步骤：**

```bash
# 1. 检查PostgreSQL状态
sudo systemctl status postgresql

# 2. 测试数据库连接
psql -h localhost -U stock_user -d stock_analysis

# 3. 检查.env配置
cat /var/www/stock-analysis/backend/.env | grep DATABASE_URL

# 4. 查看PostgreSQL日志
sudo tail -50 /var/log/postgresql/postgresql-12-main.log
```

---

## 性能优化

### 数据库优化

```bash
# 连接数据库
psql -h localhost -U stock_user -d stock_analysis

# 执行优化
VACUUM ANALYZE;

# 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

### 清理旧备份

```bash
# 清理30天前的备份
find /var/www/stock-analysis/backend/backups -name "backup_*.sql.gz" -mtime +30 -delete

# 清理Nginx日志
sudo find /var/log/nginx -name "*.log.*" -mtime +7 -delete
```

---

## 服务器信息

| 项目 | 信息 |
|------|------|
| **服务器IP** | 82.157.28.35 |
| **用户名** | ubuntu |
| **域名** | https://qwquant.com |
| **后端端口** | 8000 |
| **数据库** | stock_analysis |
| **数据库用户** | stock_user |
| **项目路径** | /var/www/stock-analysis |
| **Nginx配置** | /etc/nginx/sites-enabled/stock-analysis-domain |
| **SSL证书** | /etc/letsencrypt/live/www.qwquant.com/ |

---

## 紧急回滚

如果更新后出现严重问题，立即回滚：

### 回滚后端

```bash
ssh ubuntu@82.157.28.35

sudo systemctl stop stock-analysis-backend
cd /var/www/stock-analysis
rm -rf backend
mv backend.backup backend
sudo systemctl start stock-analysis-backend
```

### 回滚前端

```bash
ssh ubuntu@82.157.28.35

cd /var/www/stock-analysis/frontend
rm -rf dist
mv dist.backup dist
sudo systemctl reload nginx
```

### 回滚数据库

```bash
ssh ubuntu@82.157.28.35

cd /var/www/stock-analysis/backend/backups
gunzip -c backup_20251130_150000.sql.gz | PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis
```

---

## 获取帮助

- **部署文档**: `deploy/docs/DEPLOYMENT.md`
- **更新指南**: `deploy/docs/UPDATE-GUIDE.md`
- **数据库Schema**: `.spec-workflow/database-schema.md`
- **后端日志**: `sudo journalctl -u stock-analysis-backend -f`
- **Nginx日志**: `sudo tail -f /var/log/nginx/qwquant_error.log`
