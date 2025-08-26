from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Dict, Any
import uvicorn
from models.zalo_events import ZaloEvent, parse_zalo_event
from handlers.event_handler import EventHandler
from config import settings

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zalo Webhook Server",
    description="Server để nhận và xử lý các sự kiện từ Zalo OA",
    version="1.0.0",
)

# Khởi tạo event handler
event_handler = EventHandler()

# HTML template cho dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zalo Webhook Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .stat-card h3 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .stat-card p {
            color: #6c757d;
            font-size: 1.1em;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .webhook-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .webhook-info h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .webhook-url {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 1.1em;
            margin-bottom: 15px;
            word-break: break-all;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status.healthy {
            background: #d4edda;
            color: #155724;
        }
        
        .status.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Zalo Webhook Dashboard</h1>
            <p>Quản lý và theo dõi webhook từ Zalo OA</p>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3 id="total-events">-</h3>
                    <p>Tổng số events</p>
                </div>
                <div class="stat-card">
                    <h3 id="last-event">-</h3>
                    <p>Event cuối cùng</p>
                </div>
                <div class="stat-card">
                    <h3 id="server-status" class="status healthy">Online</h3>
                    <p>Trạng thái server</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📡 Webhook Configuration</h2>
                <div class="webhook-info">
                    <h3>Webhook URL</h3>
                    <div class="webhook-url" id="webhook-url">https://zalo.truongvinhkhuong.io.vn/webhook</div>
                    <p><strong>Verify Token:</strong> <span id="verify-token">***</span></p>
                    <p><strong>Secret Key:</strong> <span id="secret-key">***</span></p>
                </div>
                
                <div class="webhook-info">
                    <h3>Endpoints</h3>
                    <p><strong>Health Check:</strong> <code>/</code> - Kiểm tra trạng thái server</p>
                    <p><strong>Webhook:</strong> <code>/webhook</code> - Nhận events từ Zalo</p>
                    <p><strong>Events:</strong> <code>/events</code> - Xem danh sách events</p>
                    <p><strong>Dashboard:</strong> <code>/dashboard</code> - Giao diện quản lý</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 Quick Actions</h2>
                <a href="/events" class="btn">📊 Xem Events</a>
                <a href="/" class="btn btn-secondary">💚 Health Check</a>
                <a href="/webhook" class="btn btn-secondary">🔗 Test Webhook</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 Zalo Webhook Server | Powered by FastAPI</p>
        </div>
    </div>
    
    <script>
        // Cập nhật thông tin real-time
        async function updateStats() {
            try {
                const response = await fetch('/events');
                const data = await response.json();
                
                if (data.events) {
                    document.getElementById('total-events').textContent = data.events.length;
                    
                    if (data.events.length > 0) {
                        const lastEvent = data.events[data.events.length - 1];
                        const eventTime = new Date(lastEvent.timestamp).toLocaleString('vi-VN');
                        document.getElementById('last-event').textContent = eventTime;
                    } else {
                        document.getElementById('last-event').textContent = 'Chưa có';
                    }
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        // Cập nhật mỗi 30 giây
        updateStats();
        setInterval(updateStats, 30000);
        
        // Hiển thị verify token và secret key (ẩn một phần)
        document.getElementById('verify-token').textContent = '***' + (window.location.hostname.includes('localhost') ? 'dev' : '***');
        document.getElementById('secret-key').textContent = '***' + (window.location.hostname.includes('localhost') ? 'dev' : '***');
    </script>
</body>
</html>
"""

def verify_signature(request_body: str, signature: str) -> bool:
    """
    Xác thực chữ ký từ Zalo để đảm bảo request hợp lệ
    """
    if not settings.ZALO_SECRET_KEY:
        logger.warning("ZALO_SECRET_KEY chưa được cấu hình")
        return True  # Bỏ qua validation nếu chưa có secret key
    
    expected_signature = hmac.new(
        settings.ZALO_SECRET_KEY.encode('utf-8'),
        request_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard chính - hiển thị giao diện web thay vì JSON"""
    return HTMLResponse(content=DASHBOARD_HTML, status_code=200)

@app.get("/health")
async def health_check():
    """Health check endpoint riêng biệt cho API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Zalo Webhook Server"
    }

@app.get("/webhook")
async def webhook_verification(hub_challenge: str = None, hub_verify_token: str = None):
    """
    Endpoint để Zalo verify webhook URL
    """
    if hub_verify_token == settings.ZALO_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return hub_challenge
    else:
        logger.error(f"Webhook verification failed. Token: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Endpoint chính để nhận các sự kiện từ Zalo
    """
    try:
        # Đọc request body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Lấy signature từ header (nếu có)
        signature = request.headers.get('X-Zalo-Signature', '')
        
        # Verify signature
        if not verify_signature(body_str, signature):
            logger.error("Invalid signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON
        try:
            event_data = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        logger.info(f"Received webhook: {event_data}")
        
        # Parse event từ raw data
        zalo_event = parse_zalo_event(event_data)
        
        if zalo_event:
            # Xử lý event
            await event_handler.handle_event(zalo_event)
            logger.info(f"Successfully handled event: {zalo_event.event_name}")
        else:
            logger.warning(f"Unknown event type: {event_data}")
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Event processed"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/events")
async def get_recent_events():
    """
    Endpoint để xem các events gần đây (có thể dùng để debug)
    """
    return event_handler.get_recent_events()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
