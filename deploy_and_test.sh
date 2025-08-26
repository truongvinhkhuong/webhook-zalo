#!/bin/bash

# Script deploy và test Zalo Platform verification
echo "🚀 Deploy và test Zalo Platform verification..."

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker không được cài đặt"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose không được cài đặt"
    exit 1
fi

# Dừng container cũ nếu có
echo "🛑 Dừng container cũ..."
docker-compose down

# Build và chạy container mới
echo "🔨 Build và chạy container mới..."
docker-compose up -d --build

# Đợi container khởi động
echo "⏳ Đợi container khởi động..."
sleep 10

# Kiểm tra container có chạy không
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Container không chạy được"
    docker-compose logs
    exit 1
fi

echo "✅ Container đã chạy thành công!"

# Test các endpoints
echo ""
echo "🔍 Testing các endpoints..."

# Test health check
echo "💚 Testing health check..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Health check: OK"
else
    echo "❌ Health check: FAILED"
fi

# Test trang chủ
echo "🏠 Testing trang chủ..."
if curl -s http://localhost:8001/ | grep -q "zalo-platform-site-verification"; then
    echo "✅ Meta tag xác thực: OK"
else
    echo "❌ Meta tag xác thực: NOT FOUND"
fi

# Test dashboard
echo "📊 Testing dashboard..."
if curl -s http://localhost:8001/dashboard > /dev/null 2>&1; then
    echo "✅ Dashboard: OK"
else
    echo "❌ Dashboard: FAILED"
fi

# Test webhook endpoint
echo "🔗 Testing webhook endpoint..."
if curl -s http://localhost:8001/webhook > /dev/null 2>&1; then
    echo "✅ Webhook endpoint: OK"
else
    echo "❌ Webhook endpoint: FAILED"
fi

echo ""
echo "🎉 Deploy và test hoàn tất!"
echo ""
echo "📱 Để xác thực với Zalo Platform:"
echo "   1. Truy cập: https://zalo.truongvinhkhuong.io.vn/"
echo "   2. View source code (Ctrl+U)"
echo "   3. Tìm meta tag: zalo-platform-site-verification"
echo "   4. Click Verify trong Zalo Platform"
echo ""
echo "🔍 Để test local:"
echo "   - Trang chủ: http://localhost:8001/"
echo "   - Dashboard: http://localhost:8001/dashboard"
echo "   - Health: http://localhost:8001/health"
echo ""
echo "📊 Để xem logs:"
echo "   docker-compose logs -f"
