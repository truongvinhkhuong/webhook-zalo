from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
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

@app.get("/")
async def health_check():
    """Health check endpoint"""
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
