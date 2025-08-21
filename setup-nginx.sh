#!/bin/bash

# Script setup Nginx cho Zalo Webhook Server
# Chạy với quyền root

echo "🚀 Setting up Nginx configuration for Zalo Webhook..."

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Tạo thư mục logs nếu chưa có
mkdir -p /var/log/nginx

# Copy Nginx config
echo "📝 Copying Nginx configuration..."
cp nginx-webhook.conf /etc/nginx/sites-available/zalo-webhook

# Tạo symlink
echo "🔗 Creating symlink..."
ln -sf /etc/nginx/sites-available/zalo-webhook /etc/nginx/sites-enabled/

# Kiểm tra cấu hình Nginx
echo "🔍 Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Reload Nginx
    echo "🔄 Reloading Nginx..."
    systemctl reload nginx
    
    echo "✅ Nginx setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update your DNS to point zalo.truongvinhkhuong.io.vn to this server"
    echo "2. Get SSL certificate: sudo certbot --nginx -d zalo.truongvinhkhuong.io.vn"
    echo "3. Start Docker container: docker-compose up -d"
    echo ""
    echo "🌐 Webhook URL: https://zalo.truongvinhkhuong.io.vn/webhook"
    echo "📊 Health Check: https://zalo.truongvinhkhuong.io.vn/health"
else
    echo "❌ Nginx configuration test failed"
    echo "Please check the configuration file"
    exit 1
fi
