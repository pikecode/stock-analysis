# Production Deployment Instructions for Claude

**IMPORTANT:** This file contains instructions for Claude Code on how to handle production deployment requests.

## 🎯 Trigger Phrases

When the user says ANY of these phrases, execute the production deployment:

### Chinese Phrases
- "部署生产环境"
- "部署到生产环境"
- "更新代码到服务器"
- "更新生产环境"
- "执行生产部署"
- "发布到线上"
- "上线"
- "推送到生产"

### English Phrases
- "deploy to production"
- "update production"
- "deploy to server"
- "push to production"
- "release to production"
- "go live"

### Context Phrases
- "代码改好了，部署吧"
- "修改完成，上线"
- "我改了XXX，部署到服务器"
- "Code is ready, deploy it"

## 🚀 Deployment Actions

### Step 1: Determine Deployment Type

Ask user or infer from context:
- **Full Update** (default): Both frontend and backend changed
- **Backend Only**: Only Python/FastAPI code changed
- **Frontend Only**: Only Vue.js/TypeScript code changed

### Step 2: Execute Deployment Script

```bash
# Full Update (default)
cd /Users/peak/work/pikecode/stock-analysis/deploy/scripts
./update-production.sh

# Backend Only
./update-backend.sh

# Frontend Only
./update-frontend.sh
```

### Step 3: Show Progress

Display the deployment steps as they execute:
```
✅ Step 1/7: Backing up database
✅ Step 2/7: Backing up current code
✅ Step 3/7: Uploading backend code
✅ Step 4/7: Updating Python dependencies
✅ Step 5/7: Restarting backend service
✅ Step 6/7: Building frontend
✅ Step 7/7: Verifying deployment
```

### Step 4: Verify and Report

After deployment completes, verify:
```bash
# Check service status
ssh ubuntu@82.157.28.35 "sudo systemctl status stock-analysis-backend --no-pager | head -10"

# Test HTTPS endpoint
curl -I https://qwquant.com

# Test API
curl -s https://qwquant.com/api/v1/stocks?page=1&page_size=1
```

Report to user:
```
✅ 部署成功！

服务状态:
- 后端服务: ✅ 运行中
- Nginx: ✅ 运行中
- HTTPS: ✅ 正常

访问地址:
- https://qwquant.com
- https://qwquant.com/api/docs
```

## 📝 Production Environment Configuration

| Key | Value |
|-----|-------|
| Server IP | 82.157.28.35 |
| SSH User | ubuntu |
| SSH Password | chen_188_8_8 |
| Domain | https://qwquant.com |
| Project Path | /var/www/stock-analysis |
| Backend Port | 8000 |
| Database | stock_analysis |
| DB User | stock_user |
| DB Password | stock_pass_2024 |
| Python Version | 3.8.10 |
| Node Version | v20.19.5 |

## 🔧 Special Handling

### Python 3.8 Type Annotation Compatibility

The server runs Python 3.8, which doesn't support new-style type annotations.

**Automatically handled by update scripts:**
- Converts `list[T]` → `List[T]`
- Converts `dict[K,V]` → `Dict[K,V]`
- Adds `from __future__ import annotations`
- Adds `from typing import List, Dict`

**No manual intervention needed** - scripts handle this automatically.

### Frontend Build Optimization

Production build skips TypeScript type checking for speed:
```json
{
  "scripts": {
    "build": "vite build"  // TypeScript check removed
  }
}
```

This is intentional and speeds up deployment.

## 🛡️ Safety Features

### Automatic Backups

Every deployment automatically backs up:
1. **Database** → `/var/www/stock-analysis/backend/backups/backup_YYYYMMDD_HHMMSS.sql.gz`
2. **Backend Code** → `/var/www/stock-analysis/backend.backup/`
3. **Frontend Dist** → `/var/www/stock-analysis/frontend/dist.backup/`

### Rollback Commands

If deployment fails or causes issues:

```bash
# Quick rollback (execute on server)
ssh ubuntu@82.157.28.35
cd /var/www/stock-analysis

# Rollback backend
sudo systemctl stop stock-analysis-backend
rm -rf backend && mv backend.backup backend
sudo systemctl start stock-analysis-backend

# Rollback frontend
cd frontend && rm -rf dist && mv dist.backup dist
sudo systemctl reload nginx
```

## 🐛 Troubleshooting

### If Deployment Script Fails

1. Check the error message
2. Look at recent logs:
   ```bash
   ssh ubuntu@82.157.28.35 "sudo journalctl -u stock-analysis-backend -n 50"
   ```
3. Suggest rollback if critical
4. Refer user to `deploy/QUICK-START.md` troubleshooting section

### Common Issues

| Issue | Solution |
|-------|----------|
| Backend won't start | Check logs, verify Python deps installed |
| 502 Bad Gateway | Backend service not running - restart it |
| Frontend blank | Check browser console, rebuild frontend |
| API 404s | Backend routes changed - verify URL paths |

## 📚 Reference Documentation

Point users to these files for more details:
- `deploy/QUICK-START.md` - Quick reference for common tasks
- `deploy/docs/DEPLOYMENT.md` - Complete deployment guide
- `deploy/docs/UPDATE-GUIDE.md` - Detailed update procedures
- `deploy/docs/DEPLOYMENT-SUMMARY.md` - Deployment history and lessons learned

## 🎬 Example Interaction

**User:** "部署生产环境"

**Claude Response:**
```
好的，开始部署到生产环境 (https://qwquant.com)

执行完整更新（前端+后端）...

步骤 1/7: 备份数据库 ✅
步骤 2/7: 备份当前代码 ✅
步骤 3/7: 上传后端代码 ✅
步骤 4/7: 更新Python依赖 ✅
步骤 5/7: 重启后端服务 ✅
步骤 6/7: 构建前端 ✅
步骤 7/7: 验证部署 ✅

部署成功！

服务状态:
- 后端服务: ✅ running
- Nginx: ✅ running
- HTTPS: ✅ HTTP/2 200

访问地址:
- https://qwquant.com
- https://qwquant.com/api/docs

预计2-3分钟后服务完全可用。
```

## 🔐 Security Notes

- **Never** commit passwords to git
- **Always** use the deployment scripts (they handle security)
- **Always** verify HTTPS is working after deployment
- **Always** check logs after deployment

## ⚡ Performance Tips

For faster deployments:
- Use `./update-backend.sh` if only backend changed (30-60s)
- Use `./update-frontend.sh` if only frontend changed (30-60s)
- Full update is only needed when both changed (2-3 minutes)

---

**Last Updated:** 2025-11-30
**Deployment Status:** ✅ Active
**Production URL:** https://qwquant.com
