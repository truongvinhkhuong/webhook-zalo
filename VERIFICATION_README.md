# 🚀 Hướng dẫn xác thực Domain cho Zalo Platform

## 📋 Tổng quan
Dự án này đã được cấu hình sẵn với meta tag xác thực Zalo Platform để bạn có thể xác thực domain `zalo.truongvinhkhuong.io.vn`.

## ✅ Meta Tag đã được cấu hình
```html
<meta name="zalo-platform-site-verification" content="PyAi4-3z5aqSYvrouwutLMACZtsE-bWXDJam" />
```

## 🏗️ Cấu trúc dự án
```
webhook-zalo/
├── templates/
│   ├── index.html          # Trang chủ với meta tag xác thực
│   └── dashboard.html      # Dashboard quản lý webhook
├── app.py                  # FastAPI server
├── docker-compose.yml      # Docker configuration
└── nginx-webhook.conf      # Nginx configuration
```

## 🚀 Cách triển khai

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy với Docker (khuyến nghị)
```bash
# Build và chạy container
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f
```

### 3. Chạy trực tiếp
```bash
python app.py
```

## 🌐 Endpoints

| Endpoint | Mô tả |
|----------|-------|
| `/` | Trang chủ với meta tag xác thực |
| `/dashboard` | Dashboard quản lý webhook |
| `/health` | Health check API |
| `/webhook` | Webhook endpoint cho Zalo |
| `/events` | Danh sách events |

## 🔍 Kiểm tra meta tag

### Kiểm tra local
```bash
# Test trang chủ
curl -s "http://localhost:8001/" | grep -i "zalo-platform-site-verification"

# Test dashboard
curl -s "http://localhost:8001/dashboard" | grep -i "zalo-platform-site-verification"
```

### Kiểm tra production
```bash
# Test trang chủ
curl -s "https://zalo.truongvinhkhuong.io.vn/" | grep -i "zalo-platform-site-verification"
```

## 📱 Xác thực với Zalo Platform

### Bước 1: Kiểm tra meta tag
- Truy cập: https://zalo.truongvinhkhuong.io.vn/
- View source code (Ctrl+U)
- Tìm meta tag: `<meta name="zalo-platform-site-verification" content="PyAi4-3z5aqSYvrouwutLMACZtsE-bWXDJam" />`

### Bước 2: Xác thực
- Đăng nhập vào Zalo Platform
- Vào phần Domain Verification
- Nhập domain: `zalo.truongvinhkhuong.io.vn`
- Click "Verify"

## ⚠️ Lưu ý quan trọng

1. **Meta tag phải ở đầu trang**: Meta tag đã được đặt ở đầu thẻ `<head>` để đảm bảo Zalo có thể đọc được
2. **Kích thước trang**: Trang web được tối ưu để không vượt quá 512KB
3. **Tốc độ tải**: Sử dụng CDN và tối ưu hóa để tăng tốc độ tải trang
4. **IP nước ngoài**: Nginx đã được cấu hình để không chặn requests từ IP nước ngoài

## 🛠️ Troubleshooting

### Meta tag không hiển thị
```bash
# Kiểm tra server có chạy không
curl -f http://localhost:8001/health

# Kiểm tra logs
docker-compose logs -f
```

### Lỗi template
```bash
# Kiểm tra thư mục templates
ls -la templates/

# Kiểm tra quyền file
chmod 644 templates/*.html
```

### Lỗi nginx
```bash
# Kiểm tra cấu hình nginx
nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 📞 Hỗ trợ
Nếu gặp vấn đề, hãy kiểm tra:
1. Logs của Docker container
2. Logs của Nginx
3. Cấu hình firewall
4. SSL certificate

## 🔗 Liên kết hữu ích
- [Zalo Platform Documentation](https://developers.zalo.me/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
