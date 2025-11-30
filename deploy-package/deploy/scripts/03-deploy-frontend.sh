#!/bin/bash
# ========================================
# 前端部署脚本
# ========================================

set -e

# 配置变量
PROJECT_DIR="/var/www/stock-analysis"
FRONTEND_DIR="$PROJECT_DIR/frontend"
NGINX_SITE_CONF="/etc/nginx/sites-available/stock-analysis"

echo "========================================="
echo "开始部署前端服务..."
echo "========================================="

# 1. 复制前端代码
echo "步骤 1/5: 复制前端代码..."
rsync -av --delete \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='.env.local' \
    ../../frontend/ $FRONTEND_DIR/

# 2. 安装依赖
echo "步骤 2/5: 安装前端依赖..."
cd $FRONTEND_DIR
npm install

# 3. 构建生产版本
echo "步骤 3/5: 构建生产版本..."
npm run build

# 4. 配置Nginx
echo "步骤 4/5: 配置Nginx..."
sudo tee $NGINX_SITE_CONF > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # 修改为实际域名

    # 前端静态文件
    location / {
        root /var/www/stock-analysis/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;

        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日志
    access_log /var/log/nginx/stock-analysis.access.log;
    error_log /var/log/nginx/stock-analysis.error.log;
}
EOF

# 5. 启用站点并重启Nginx
echo "步骤 5/5: 启用站点并重启Nginx..."
sudo ln -sf $NGINX_SITE_CONF /etc/nginx/sites-enabled/stock-analysis
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "========================================="
echo "前端部署完成！"
echo "========================================="
echo "静态文件目录: $FRONTEND_DIR/dist"
echo "Nginx配置: $NGINX_SITE_CONF"
echo "访问地址: http://服务器IP"
echo "========================================="
