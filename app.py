from fastapi import FastAPI, Request, HTTPException
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, Response
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
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, JSON, Index

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

# Khởi tạo Jinja2 templates
templates = Jinja2Templates(directory="templates")

# ===================== Database setup (SQLAlchemy Async) =====================
class Base(DeclarativeBase):
    pass

class ImageMessageEvent(Base):
    __tablename__ = "image_message_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id_by_app: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(64), nullable=False)
    recipient_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_name: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    msg_id: Mapped[str] = mapped_column(String(128), nullable=True)
    text: Mapped[str] = mapped_column(String(2048), nullable=True)
    attachments: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_image_msg_user_time", "user_id_by_app", "timestamp"),
    )

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    try:
        await init_models()
        logger.info("Database tables ensured")
    except Exception as e:
        logger.error(f"Failed to init database: {e}")

def verify_signature(request_body: str, signature: str) -> bool:
    """
    Xác thực chữ ký từ Zalo để đảm bảo request hợp lệ
    """
    # Cho phép tắt bắt buộc chữ ký khi REQUIRE_SIGNATURE=False
    if not settings.REQUIRE_SIGNATURE:
        return True
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
async def home(request: Request):
    """Trang chủ với meta tag xác thực Zalo Platform"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard quản lý webhook"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/og-image.png")
async def og_image():
    """Trả về PNG nhỏ làm ảnh chia sẻ (1200x630 đề xuất, nhưng dùng ảnh nhỏ tối giản)."""
    # 1x1 transparent PNG bytes
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return Response(content=png_bytes, media_type="image/png")

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
    # Kiểm tra nếu có verify token được cấu hình
    if not settings.ZALO_VERIFY_TOKEN:
        logger.warning("ZALO_VERIFY_TOKEN chưa được cấu hình, bỏ qua verification")
        return hub_challenge
    
    # Kiểm tra nếu có token từ request
    if not hub_verify_token:
        logger.error("Webhook verification failed. No token provided")
        raise HTTPException(status_code=403, detail="No verification token provided")
    
    if hub_verify_token == settings.ZALO_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return hub_challenge
    else:
        logger.error(f"Webhook verification failed. Token: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint chính để nhận các sự kiện từ Zalo
    """
    try:
        # Đọc request body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Lấy signature từ header (Zalo có thể dùng 'X-Zalo-Signature' hoặc 'X-ZSign')
        signature = (
            request.headers.get('X-Zalo-Signature')
            or request.headers.get('X-ZSign')
            or ''
        )
        
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
            # Đưa việc xử lý vào background để phản hồi 200 sớm cho Zalo
            background_tasks.add_task(event_handler.handle_event, zalo_event)
            logger.info(f"Queued event for async handling: {zalo_event.event_name}")
        else:
            logger.warning(f"Unknown event type: {event_data}")
        
        # Trả về 200 ngay lập tức theo khuyến nghị của Zalo
        return JSONResponse(status_code=200, content={"message": "ok"})
        
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
