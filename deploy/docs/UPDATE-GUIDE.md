# 代码更新部署指南

本文档介绍如何在已部署的生产环境中更新代码。

## 快速更新（推荐）

### 方式一：使用自动化脚本

```bash
# 在本地项目根目录执行
cd /Users/peak/work/pikecode/stock-analysis/deploy/scripts

# 执行更新脚本
./update-production.sh
```

这个脚本会自动完成：
- ✅ 创建数据库备份
- ✅ 上传最新代码
- ✅ 更新后端依赖
- ✅ 重新构建前端
- ✅ 重启服务
- ✅ 验证部署结果

### 方式二：分步更新

如果需要更精细的控制，可以分步执行：

#### 1. 仅更新后端
```bash
./update-backend.sh
```

#### 2. 仅更新前端
```bash
./update-frontend.sh
```

## 详细步骤说明

### 步骤1: 备份数据库（重要！）

```bash
ssh ubuntu@82.157.28.35
cd /var/www/stock-analysis/backend
source venv/bin/activate

# 备份数据库
PGPASSWORD=stock_pass_2024 pg_dump -h localhost -U stock_user stock_analysis > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份文件
gzip backup_*.sql

# 查看备份文件
ls -lh backup_*.sql.gz
```

### 步骤2: 更新后端代码

```bash
# 在本地执行
cd /Users/peak/work/pikecode/stock-analysis

# 上传后端代码（排除虚拟环境和配置文件）
rsync -avz --exclude='venv' --exclude='.env' --exclude='__pycache__' \
  backend/ ubuntu@82.157.28.35:/var/www/stock-analysis/backend/
```

### 步骤3: 更新Python依赖（如果有变化）

```bash
# SSH到服务器
ssh ubuntu@82.157.28.35

cd /var/www/stock-analysis/backend
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 如果有数据库迁移
# alembic upgrade head
```

### 步骤4: 重启后端服务

```bash
# 在服务器上执行
sudo systemctl restart stock-analysis-backend

# 查看服务状态
sudo systemctl status stock-analysis-backend

# 查看日志
sudo journalctl -u stock-analysis-backend -f
```

### 步骤5: 更新前端代码

```bash
# 在本地执行
cd /Users/peak/work/pikecode/stock-analysis

# 上传前端代码
rsync -avz --exclude='node_modules' --exclude='dist' \
  frontend/ ubuntu@82.157.28.35:/var/www/stock-analysis/frontend/
```

### 步骤6: 重新构建前端

```bash
# SSH到服务器
ssh ubuntu@82.157.28.35

cd /var/www/stock-analysis/frontend

# 安装依赖（首次或package.json有变化时）
npm install

# 构建生产版本
npm run build

# 重启Nginx
sudo systemctl reload nginx
```

### 步骤7: 验证部署

```bash
# 在服务器上执行
curl -I https://qwquant.com
curl -s https://qwquant.com/api/v1/stocks?page=1&page_size=1
```

或访问浏览器：
- https://qwquant.com
- https://qwquant.com/api/docs

## 回滚操作

如果更新后出现问题，可以快速回滚：

### 回滚后端代码

```bash
# 假设之前的代码在 /var/www/stock-analysis/backend.backup
ssh ubuntu@82.157.28.35

sudo systemctl stop stock-analysis-backend
mv /var/www/stock-analysis/backend /var/www/stock-analysis/backend.failed
mv /var/www/stock-analysis/backend.backup /var/www/stock-analysis/backend
sudo systemctl start stock-analysis-backend
```

### 回滚数据库

```bash
ssh ubuntu@82.157.28.35

# 恢复最近的备份
cd /var/www/stock-analysis/backend
gunzip -c backup_20251130_150000.sql.gz | PGPASSWORD=stock_pass_2024 psql -h localhost -U stock_user -d stock_analysis
```

### 回滚前端

```bash
ssh ubuntu@82.157.28.35

rm -rf /var/www/stock-analysis/frontend/dist
mv /var/www/stock-analysis/frontend/dist.backup /var/www/stock-analysis/frontend/dist
sudo systemctl reload nginx
```

## 常见问题

### Q1: 后端服务启动失败

```bash
# 查看详细日志
sudo journalctl -u stock-analysis-backend -n 100

# 常见原因：
# 1. Python依赖问题 - 重新安装依赖
# 2. 数据库连接失败 - 检查.env配置
# 3. 端口被占用 - sudo netstat -tuln | grep 8000
```

### Q2: 前端构建失败

```bash
# 跳过TypeScript检查
cd /var/www/stock-analysis/frontend
sed -i 's/"build": "vue-tsc && vite build"/"build": "vite build"/g' package.json
npm run build
```

### Q3: Nginx 502 Bad Gateway

```bash
# 检查后端服务是否运行
sudo systemctl status stock-analysis-backend

# 检查端口
sudo netstat -tuln | grep 8000

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/qwquant_error.log
```

## 最佳实践

### 1. 更新前的准备

- ✅ 在测试环境验证过代码
- ✅ 备份数据库
- ✅ 通知用户（如果需要）
- ✅ 选择低峰时段

### 2. 更新过程中

- ✅ 使用自动化脚本减少人为错误
- ✅ 保留旧版本代码便于回滚
- ✅ 监控日志和服务状态
- ✅ 分步验证每个环节

### 3. 更新后

- ✅ 全面测试关键功能
- ✅ 检查错误日志
- ✅ 监控系统性能
- ✅ 记录更新内容

## 自动化部署建议

考虑设置CI/CD流程：

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: ./deploy/scripts/update-production.sh
```

## 定期维护

### 每周

- 检查磁盘空间
- 检查日志文件大小
- 清理旧的备份文件（保留最近30天）

### 每月

- 更新系统软件包: `sudo apt update && sudo apt upgrade`
- 检查SSL证书有效期
- 审查错误日志

### 每季度

- 数据库优化: `VACUUM ANALYZE`
- 清理未使用的Docker镜像（如果使用）
- 审查安全更新
