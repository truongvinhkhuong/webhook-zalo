from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import hashlib
import hmac
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """
    Middleware để giới hạn số lượng requests per minute
    """
    def __init__(self):
        self.requests = defaultdict(deque)
        self.window_size = timedelta(minutes=1)
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Kiểm tra xem client có bị rate limit không"""
        now = datetime.now()
        
        # Xóa các requests cũ (ngoài window)
        while (self.requests[client_ip] and 
               now - self.requests[client_ip][0] > self.window_size):
            self.requests[client_ip].popleft()
        
        # Kiểm tra số lượng requests trong window
        if len(self.requests[client_ip]) >= settings.MAX_EVENTS_PER_MINUTE:
            return True
        
        # Thêm request hiện tại
        self.requests[client_ip].append(now)
        return False

class SecurityValidation:
    """
    Class để validate các yêu cầu bảo mật
    """
    
    @staticmethod
    def validate_zalo_signature(request_body: str, signature: str) -> bool:
        """
        Validate signature từ Zalo
        """
        if not settings.ZALO_SECRET_KEY:
            logger.warning("ZALO_SECRET_KEY not configured, skipping signature validation")
            return True
        
        if not signature:
            logger.error("No signature provided")
            return False
        
        # Tính toán expected signature
        expected_signature = hmac.new(
            settings.ZALO_SECRET_KEY.encode('utf-8'),
            request_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # So sánh signatures
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.error(f"Signature mismatch. Expected: {expected_signature}, Got: {signature}")
        
        return is_valid
    
    @staticmethod
    def validate_request_headers(request: Request) -> bool:
        """
        Validate request headers
        """
        # Kiểm tra Content-Type
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            logger.warning(f"Invalid content type: {content_type}")
            return False
        
        # Kiểm tra User-Agent (Zalo thường có user-agent đặc biệt)
        user_agent = request.headers.get("user-agent", "")
        if not user_agent:
            logger.warning("No user-agent header")
            return False
        
        return True
    
    @staticmethod
    def validate_request_size(request_body: bytes) -> bool:
        """
        Validate kích thước request
        """
        max_size = 10 * 1024 * 1024  # 10MB
        
        if len(request_body) > max_size:
            logger.error(f"Request too large: {len(request_body)} bytes")
            return False
        
        return True

class WebhookSecurity:
    """
    Main security class tích hợp tất cả các validation
    """
    
    def __init__(self):
        self.rate_limiter = RateLimitMiddleware()
        
    async def validate_webhook_request(self, request: Request) -> bool:
        """
        Validate toàn bộ webhook request
        """
        try:
            # 1. Rate limiting
            client_ip = request.client.host if request.client else "unknown"
            if self.rate_limiter.is_rate_limited(client_ip):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # 2. Validate headers
            if not SecurityValidation.validate_request_headers(request):
                raise HTTPException(status_code=400, detail="Invalid headers")
            
            # 3. Validate request size
            body = await request.body()
            if not SecurityValidation.validate_request_size(body):
                raise HTTPException(status_code=413, detail="Request too large")
            
            # 4. Validate signature (sẽ được check trong main handler)
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security validation error: {str(e)}")
            raise HTTPException(status_code=500, detail="Security validation failed")
