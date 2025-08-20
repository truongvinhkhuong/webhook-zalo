import logging
from typing import Dict, Any, Optional
import json
import re

from models.zalo_events import (
    UserSendTextEvent, UserSendImageEvent, UserSendFileEvent,
    UserSendStickerEvent, UserSendLocationEvent
)

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Handler để xử lý các sự kiện tin nhắn từ người dùng
    """
    
    def __init__(self):
        # Có thể khởi tạo AI service, database connection, etc.
        self.command_handlers = {
            "/start": self._handle_start_command,
            "/help": self._handle_help_command,
            "/info": self._handle_info_command,
        }
    
    async def handle_message_event(self, event) -> bool:
        """
        Xử lý các sự kiện tin nhắn
        """
        try:
            event_type = type(event).__name__
            logger.info(f"Processing message event: {event_type}")
            
            if isinstance(event, UserSendTextEvent):
                return await self._handle_text_message(event)
            elif isinstance(event, UserSendImageEvent):
                return await self._handle_image_message(event)
            elif isinstance(event, UserSendFileEvent):
                return await self._handle_file_message(event)
            elif isinstance(event, UserSendStickerEvent):
                return await self._handle_sticker_message(event)
            elif isinstance(event, UserSendLocationEvent):
                return await self._handle_location_message(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}")
            return False
    
    async def _handle_text_message(self, event: UserSendTextEvent) -> bool:
        """Xử lý tin nhắn text"""
        message_text = event.message.text
        user_id = event.user_id_by_app
        sender_name = event.sender.name
        
        logger.info(f"Text message from {sender_name} ({user_id}): {message_text}")
        
        # Xử lý commands
        if message_text.startswith("/"):
            return await self._handle_command(message_text, event)
        
        # Xử lý tin nhắn thông thường
        return await self._handle_normal_text(message_text, event)
    
    async def _handle_command(self, command: str, event: UserSendTextEvent) -> bool:
        """Xử lý các commands từ người dùng"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd in self.command_handlers:
            return await self.command_handlers[cmd](event, parts[1:] if len(parts) > 1 else [])
        else:
            logger.info(f"Unknown command: {cmd}")
            # Có thể gửi tin nhắn "Lệnh không được hỗ trợ" về cho user
            return await self._send_response(
                event.user_id_by_app, 
                f"Lệnh '{cmd}' không được hỗ trợ. Gửi /help để xem danh sách lệnh."
            )
    
    async def _handle_start_command(self, event: UserSendTextEvent, args: list) -> bool:
        """Xử lý lệnh /start"""
        user_name = event.sender.name or "Bạn"
        response = f"Xin chào {user_name}! 👋\n\nChào mừng bạn đến với dịch vụ của chúng tôi.\nGửi /help để xem các lệnh có sẵn."
        
        return await self._send_response(event.user_id_by_app, response)
    
    async def _handle_help_command(self, event: UserSendTextEvent, args: list) -> bool:
        """Xử lý lệnh /help"""
        help_text = """📋 Danh sách lệnh có sẵn:

/start - Bắt đầu sử dụng dịch vụ
/help - Hiển thị trợ giúp
/info - Thông tin về hệ thống

Bạn cũng có thể gửi tin nhắn thông thường và chúng tôi sẽ phản hồi."""
        
        return await self._send_response(event.user_id_by_app, help_text)
    
    async def _handle_info_command(self, event: UserSendTextEvent, args: list) -> bool:
        """Xử lý lệnh /info"""
        info_text = f"""ℹ️ Thông tin hệ thống:

🆔 User ID: {event.user_id_by_app}
📱 App ID: {event.app_id}
⏰ Thời gian: {event.timestamp}
👤 Tên: {event.sender.name or 'Không có'}

Hệ thống đang hoạt động bình thường! ✅"""
        
        return await self._send_response(event.user_id_by_app, info_text)
    
    async def _handle_normal_text(self, text: str, event: UserSendTextEvent) -> bool:
        """Xử lý tin nhắn text thông thường"""
        user_id = event.user_id_by_app
        
        # Ở đây bạn có thể:
        # 1. Tích hợp với AI/chatbot
        # 2. Xử lý business logic
        # 3. Tìm kiếm trong database
        # 4. Gọi external APIs
        
        # Example: Echo response với một số xử lý đơn giản
        if "hello" in text.lower() or "xin chào" in text.lower():
            response = "Xin chào! Tôi có thể giúp gì cho bạn? 😊"
        elif "cảm ơn" in text.lower() or "thank" in text.lower():
            response = "Không có gì! Rất vui được giúp đỡ bạn! 🤗"
        else:
            response = f"Bạn vừa gửi: '{text}'\n\nTôi đã nhận được tin nhắn của bạn. Cảm ơn bạn! 📝"
        
        return await self._send_response(user_id, response)
    
    async def _handle_image_message(self, event: UserSendImageEvent) -> bool:
        """Xử lý tin nhắn hình ảnh"""
        user_id = event.user_id_by_app
        attachments = event.message.attachments
        
        logger.info(f"Image message from {user_id}: {len(attachments) if attachments else 0} attachments")
        
        # Xử lý hình ảnh
        # Có thể download, phân tích, OCR, etc.
        
        response = "Tôi đã nhận được hình ảnh của bạn! 📸\n\nChức năng xử lý hình ảnh đang được phát triển."
        return await self._send_response(user_id, response)
    
    async def _handle_file_message(self, event: UserSendFileEvent) -> bool:
        """Xử lý tin nhắn file"""
        user_id = event.user_id_by_app
        attachments = event.message.attachments
        
        logger.info(f"File message from {user_id}: {len(attachments) if attachments else 0} files")
        
        response = "Tôi đã nhận được file của bạn! 📎\n\nChức năng xử lý file đang được phát triển."
        return await self._send_response(user_id, response)
    
    async def _handle_sticker_message(self, event: UserSendStickerEvent) -> bool:
        """Xử lý tin nhắn sticker"""
        user_id = event.user_id_by_app
        
        logger.info(f"Sticker message from {user_id}")
        
        response = "Sticker đẹp quá! 😄"
        return await self._send_response(user_id, response)
    
    async def _handle_location_message(self, event: UserSendLocationEvent) -> bool:
        """Xử lý tin nhắn vị trí"""
        user_id = event.user_id_by_app
        
        logger.info(f"Location message from {user_id}")
        
        # Xử lý location data
        # Có thể lưu vào database, tìm kiếm nearby services, etc.
        
        response = "Tôi đã nhận được vị trí của bạn! 📍\n\nChức năng xử lý vị trí đang được phát triển."
        return await self._send_response(user_id, response)
    
    async def _send_response(self, user_id: str, message: str) -> bool:
        """
        Gửi phản hồi về cho người dùng qua Zalo API
        
        Note: Đây là placeholder. Bạn cần implement thực tế với Zalo Send API
        """
        try:
            logger.info(f"Sending response to {user_id}: {message}")
            
            # TODO: Implement actual Zalo Send API call
            # Ví dụ:
            # await zalo_api.send_message(user_id, message)
            
            # Hiện tại chỉ log để test
            logger.info("Response logged (not sent - Zalo Send API not implemented yet)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            return False
