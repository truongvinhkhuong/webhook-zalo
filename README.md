# Zalo Webhook Server

Hệ thống nhận và xử lý các sự kiện (events) được Zalo gửi qua HTTP POST đến Webhook URL.

## Tính năng

- ✅ Nhận và xử lý các sự kiện từ Zalo Official Account
- ✅ Xử lý tin nhắn text, hình ảnh, file, sticker, vị trí
- ✅ Xử lý sự kiện follow/unfollow, submit info, click button
- ✅ Validation signature để đảm bảo bảo mật
- ✅ Rate limiting để tránh spam
- ✅ Logging chi tiết
- ✅ API documentation tự động (FastAPI)
- ✅ Health check endpoint

## Yêu cầu

- Python 3.8+
- Zalo Official Account
- SSL certificate cho domain
- Server có thể truy cập từ Internet

## ⚡ Cài đặt nhanh

### 1. Clone và cài đặt dependencies

```bash
git clone <repository-url>
cd webhook-zalo
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

```bash
cp .env.example .env
# Chỉnh sửa file .env với thông tin của bạn
```

### 3. Chạy server

```bash
# Development
python app.py

# Production
uvicorn app:app --host 0.0.0.0 --port 8000
```

## ⚙️ Cấu hình

### Environment Variables

Tạo file `.env` từ `.env.example` và cập nhật các giá trị:

```env
# Server Configuration
PORT=8000
DEBUG=False

# Zalo Webhook Configuration
ZALO_SECRET_KEY=your_zalo_secret_key_here
ZALO_VERIFY_TOKEN=your_verify_token_here
ZALO_APP_ID=your_app_id_here
ZALO_OA_ID=your_oa_id_here

# Webhook Domain
WEBHOOK_DOMAIN=zalo.truongvinhkhuong.io.vn
```

### Lấy thông tin từ Zalo

1. Đăng nhập [Zalo Developers](https://developers.zalo.me/)
2. Tạo ứng dụng mới hoặc chọn ứng dụng hiện có
3. Vào **Official Account** > **Webhook**
4. Lấy các thông tin:
   - `App ID`: ID của ứng dụng
   - `OA ID`: ID của Official Account
   - `Secret Key`: Key để verify signature
   - `Verify Token`: Token để verify webhook URL

## Cấu hình Webhook trên Zalo

### 1. Thiết lập Webhook URL

- Webhook URL: `https://zalo.truongvinhkhuong.io.vn/webhook`
- Verify Token: Sử dụng giá trị `ZALO_VERIFY_TOKEN` từ file `.env`

### 2. Đăng ký Events

Trong phần **Webhook Events**, chọn các events muốn nhận:

- `user_send_text` - Người dùng gửi tin nhắn text
- `user_send_image` - Người dùng gửi hình ảnh
- `user_send_file` - Người dùng gửi file
- `user_send_sticker` - Người dùng gửi sticker
- `user_send_location` - Người dùng gửi vị trí
- `follow` - Người dùng follow OA
- `unfollow` - Người dùng unfollow OA
- `user_submit_info` - Người dùng submit thông tin
- `user_click_button` - Người dùng click button

## Cấu trúc Project

```
webhook-zalo/
├── app.py                 # FastAPI application chính
├── config.py             # Cấu hình từ environment variables
├── middleware.py         # Security middleware
├── requirements.txt      # Python dependencies
├── .env.example         # Template cho environment variables
├── README.md           # Documentation
├── models/
│   ├── __init__.py
│   └── zalo_events.py  # Data models cho Zalo events
└── handlers/
    ├── __init__.py
    ├── event_handler.py      # Main event handler
    ├── message_handler.py    # Xử lý tin nhắn
    └── user_action_handler.py # Xử lý hành động user
```

## 🔍 API Endpoints

### Health Check
```
GET /
```
Kiểm tra trạng thái server.

### Webhook Verification
```
GET /webhook?hub.challenge=XXX&hub.verify_token=YYY
```
Endpoint để Zalo verify webhook URL.

### Webhook Events
```
POST /webhook
```
Endpoint nhận events từ Zalo.

### Recent Events (Debug)
```
GET /events
```
Xem các events gần đây (để debug).

### API Documentation
```
GET /docs
```
FastAPI tự động tạo API documentation.

## 🚀 Deployment

### Option 1: Docker

Tạo `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Chạy với Docker:

```bash
docker build -t zalo-webhook .
docker run -p 8000:8000 --env-file .env zalo-webhook
```

### Option 2: Systemd Service

Tạo file `/etc/systemd/system/zalo-webhook.service`:

```ini
[Unit]
Description=Zalo Webhook Server
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/webhook-zalo
Environment=PATH=/path/to/venv/bin
EnvironmentFile=/path/to/webhook-zalo/.env
ExecStart=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 3: Nginx Proxy

Cấu hình Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name zalo.truongvinhkhuong.io.vn;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Logging

Logs được lưu vào:
- Console output
- File `webhook.log`

Cấu hình log level thông qua `LOG_LEVEL` environment variable.

## 🛠️ Tùy chỉnh

### Thêm xử lý tin nhắn

Chỉnh sửa `handlers/message_handler.py`:

```python
async def _handle_normal_text(self, text: str, event: UserSendTextEvent) -> bool:
    # Thêm logic xử lý tin nhắn của bạn ở đây
    if "đặt hàng" in text.lower():
        return await self._handle_order_request(text, event)
    
    return await self._send_response(event.user_id_by_app, "Tôi đã nhận được tin nhắn của bạn!")
```

### Thêm database

Uncomment các dòng database trong `requirements.txt` và thêm models:

```python
# models/database.py
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class EventLog(Base):
    __tablename__ = "event_logs"
    
    id = Column(String, primary_key=True)
    event_name = Column(String, index=True)
    user_id = Column(String, index=True)
    data = Column(Text)
    timestamp = Column(DateTime)
```

## Debug

### Kiểm tra logs
```bash
tail -f webhook.log
```

### Test webhook locally
```bash
# Sử dụng ngrok để expose local server
ngrok http 8000

# Cập nhật webhook URL trên Zalo với URL từ ngrok
```

### Kiểm tra recent events
```bash
curl https://zalo.truongvinhkhuong.io.vn/events
```

## Bảo mật

- Signature verification với HMAC-SHA256
- Rate limiting (100 requests/minute mặc định)
- Request size limiting (10MB max)
- Header validation
- HTTPS required cho production

## Hỗ trợ

Nếu gặp vấn đề, check:

1. **Webhook không nhận được events**
   - Kiểm tra URL có accessible từ Internet không
   - Verify token có đúng không
   - SSL certificate có hợp lệ không

2. **Signature validation fail**
   - Kiểm tra `ZALO_SECRET_KEY` có đúng không
   - Đảm bảo secret key không có space thừa

3. **Server error**
   - Check logs trong `webhook.log`
   - Kiểm tra environment variables
   - Đảm bảo dependencies đã được cài đặt đầy đủ


