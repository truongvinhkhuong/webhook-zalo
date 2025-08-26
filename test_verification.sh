#!/bin/bash

# Script test meta tag xác thực Zalo Platform
echo "🔍 Kiểm tra meta tag xác thực Zalo Platform..."

# Test trang chủ
echo "📄 Testing trang chủ (/)..."
curl -s "http://localhost:8001/" | grep -i "zalo-platform-site-verification"

# Test dashboard
echo "📊 Testing dashboard (/dashboard)..."
curl -s "http://localhost:8001/dashboard" | grep -i "zalo-platform-site-verification"

# Test health check
echo "💚 Testing health check (/health)..."
curl -s "http://localhost:8001/health"

echo ""
echo "✅ Test hoàn tất!"
echo "📝 Để xem meta tag, hãy truy cập: http://localhost:8001/"
echo "🔗 Hoặc sử dụng: curl -s http://localhost:8001/ | grep -A1 -B1 'zalo-platform-site-verification'"
