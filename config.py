import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Cấu hình ứng dụng từ environment variables
    """
    # Server settings
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Zalo webhook settings
    ZALO_SECRET_KEY: Optional[str] = os.getenv("ZALO_SECRET_KEY")
    ZALO_VERIFY_TOKEN: Optional[str] = os.getenv("ZALO_VERIFY_TOKEN")
    ZALO_APP_ID: Optional[str] = os.getenv("ZALO_APP_ID")
    ZALO_OA_ID: Optional[str] = os.getenv("ZALO_OA_ID")
    REQUIRE_SIGNATURE: bool = os.getenv("REQUIRE_SIGNATURE", "False").lower() == "true"
    
    # Database settings (nếu cần lưu trữ events)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Webhook domain
    WEBHOOK_DOMAIN: str = os.getenv("WEBHOOK_DOMAIN", "zalo.truongvinhkhuong.io.vn")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting
    MAX_EVENTS_PER_MINUTE: int = int(os.getenv("MAX_EVENTS_PER_MINUTE", "100"))

    class Config:
        env_file = ".env"
        case_sensitive = True

# Khởi tạo settings singleton
settings = Settings()
