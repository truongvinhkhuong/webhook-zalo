# Zalo Webhook Server

Server để nhận và xử lý các sự kiện từ Zalo OA (Official Account).

## Tính năng

- **Webhook Endpoint**: Nhận và xử lý events từ Zalo
- **Dashboard Web**: Giao diện quản lý đẹp mắt với thống kê real-time
- **Health Check**: Kiểm tra trạng thái server
- **Event Logging**: Lưu trữ và xem lại các events
- **Security**: Xác thực chữ ký từ Zalo
- **Docker Support**: Dễ dàng deploy và scale

## Endpoints

| Endpoint | Mô tả | Response |
|----------|-------|----------|
| `/` | Dashboard chính | HTML Dashboard |
| `/health` | Health check API | JSON |
| `/webhook` | Webhook endpoint | Text/JSON |
| `/events` | Danh sách events | JSON |

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd webhook-zalo
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment
```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin Zalo của bạn
```

### 4. Chạy với Docker (Khuyến nghị)
```bash
# Build và chạy
docker-compose up -d

# Hoặc sử dụng script restart
./restart_service.sh
```

### 5. Chạy trực tiếp
```bash
python run.py
```

## Cấu hình

### Environment Variables

Tạo file `.env` với các biến sau:

```env
# Zalo Configuration
ZALO_VERIFY_TOKEN=your_verify_token_here
ZALO_SECRET_KEY=your_secret_key_here

# Server Configuration
PORT=8000
DEBUG=False

# Optional: Database
# DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Nginx Configuration

File `nginx-webhook.conf` đã được cấu hình sẵn với:
- SSL/TLS support
- Security headers
- Proxy to Docker container
- Health check endpoint

## Dashboard

Dashboard web cung cấp:

- **Thống kê real-time**: Số lượng events, event cuối cùng
- **Trạng thái server**: Online/Offline status
- **Cấu hình webhook**: URL, tokens, endpoints
- **Quick actions**: Các nút truy cập nhanh

Truy cập: `https://your-domain.com/`

## Security

- **Signature Verification**: Xác thực chữ ký từ Zalo
- **HTTPS Only**: Redirect HTTP to HTTPS
- **Security Headers**: X-Frame-Options, XSS Protection, etc.
- **Rate Limiting**: Có thể cấu hình thêm

## Logs

Logs được lưu trong:
- `webhook.log` - Application logs
- `/var/log/nginx/` - Nginx access/error logs

## Docker

### Build image
```bash
docker build -t zalo-webhook .
```

### Run container
```bash
docker run -d \
  -p 8001:8000 \
  --env-file .env \
  --name zalo-webhook \
  zalo-webhook
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing

### Test health check
```bash
curl https://your-domain.com/health
```

### Test webhook (GET)
```bash
curl "https://your-domain.com/webhook?hub_challenge=test&hub_verify_token=your_token"
```

### Test webhook (POST)
```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Zalo-Signature: your_signature" \
  -d '{"event_name": "test"}'
```

## 📁 Cấu trúc Project

```
webhook-zalo/
├── app.py                 # Main FastAPI application
├── config.py             # Configuration settings
├── docker-compose.yml    # Docker services
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
├── nginx-webhook.conf   # Nginx configuration
├── restart_service.sh   # Service restart script
├── handlers/            # Event handlers
├── models/              # Data models
└── logs/               # Application logs
```

## Troubleshooting

### Service không khởi động
```bash
# Kiểm tra logs
docker-compose logs

# Restart service
./restart_service.sh
```

### Nginx errors
```bash
# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Port conflicts
```bash
# Kiểm tra port usage
sudo netstat -tlnp | grep :8001

# Thay đổi port trong docker-compose.yml
```

## 📈 Monitoring

- **Health Check**: `/health` endpoint
- **Metrics**: Số lượng events, response time
- **Logs**: Application và nginx logs
- **Status**: Dashboard real-time

## Updates

Để cập nhật service:

```bash
# Pull latest code
git pull

# Restart với code mới
./restart_service.sh
```



