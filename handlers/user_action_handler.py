import logging
from typing import Dict, Any
from datetime import datetime

from models.zalo_events import (
    FollowOAEvent, UnfollowOAEvent, UserSubmitInfoEvent, UserClickButtonEvent
)

logger = logging.getLogger(__name__)

class UserActionHandler:
    """
    Handler để xử lý các sự kiện hành động của người dùng
    """
    
    def __init__(self):
        # Có thể khởi tạo database connection, external services, etc.
        pass
    
    async def handle_user_action_event(self, event) -> bool:
        """
        Xử lý các sự kiện hành động của người dùng
        """
        try:
            event_type = type(event).__name__
            logger.info(f"Processing user action event: {event_type}")
            
            if isinstance(event, FollowOAEvent):
                return await self._handle_follow_event(event)
            elif isinstance(event, UnfollowOAEvent):
                return await self._handle_unfollow_event(event)
            elif isinstance(event, UserSubmitInfoEvent):
                return await self._handle_submit_info_event(event)
            elif isinstance(event, UserClickButtonEvent):
                return await self._handle_button_click_event(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling user action event: {str(e)}")
            return False
    
    async def _handle_follow_event(self, event: FollowOAEvent) -> bool:
        """Xử lý sự kiện người dùng follow OA"""
        user_id = event.user_id_by_app
        follower = event.follower
        
        logger.info(f"User {follower.name} ({user_id}) followed OA")
        
        # Lưu thông tin người follow vào database
        await self._save_follower_info(user_id, follower, "follow")
        
        # Gửi tin nhắn chào mừng
        welcome_message = f"""🎉 Chào mừng {follower.name or 'bạn'} đến với Official Account của chúng tôi!

Cảm ơn bạn đã theo dõi. Chúng tôi sẽ cập nhật những thông tin mới nhất và hữu ích cho bạn.

Gửi /help để xem các lệnh có sẵn."""
        
        # TODO: Gửi welcome message qua Zalo Send API
        logger.info(f"Welcome message for {user_id}: {welcome_message}")
        
        return True
    
    async def _handle_unfollow_event(self, event: UnfollowOAEvent) -> bool:
        """Xử lý sự kiện người dùng unfollow OA"""
        user_id = event.user_id_by_app
        follower = event.follower
        
        logger.info(f"User {follower.name} ({user_id}) unfollowed OA")
        
        # Cập nhật status trong database
        await self._save_follower_info(user_id, follower, "unfollow")
        
        # Có thể trigger một số cleanup tasks
        # Ví dụ: xóa scheduled messages, dừng notifications, etc.
        
        return True
    
    async def _handle_submit_info_event(self, event: UserSubmitInfoEvent) -> bool:
        """Xử lý sự kiện người dùng submit thông tin"""
        user_id = event.user_id_by_app
        info = event.info
        sender = event.sender
        
        logger.info(f"User {sender.name} ({user_id}) submitted info: {info}")
        
        # Xử lý thông tin được submit
        # Có thể là form data, survey response, registration info, etc.
        
        # Lưu thông tin vào database
        await self._save_user_submitted_info(user_id, info)
        
        # Xác nhận đã nhận được thông tin
        confirmation_message = "✅ Cảm ơn bạn đã gửi thông tin!\n\nChúng tôi đã nhận được và sẽ xử lý sớm nhất có thể."
        
        # TODO: Gửi confirmation message
        logger.info(f"Confirmation message for {user_id}: {confirmation_message}")
        
        return True
    
    async def _handle_button_click_event(self, event: UserClickButtonEvent) -> bool:
        """Xử lý sự kiện người dùng click button"""
        user_id = event.user_id_by_app
        message = event.message
        sender = event.sender
        
        logger.info(f"User {sender.name} ({user_id}) clicked button")
        
        # Phân tích button được click
        button_payload = self._extract_button_payload(message)
        
        if button_payload:
            return await self._handle_button_payload(user_id, button_payload)
        
        return True
    
    def _extract_button_payload(self, message) -> Dict[str, Any]:
        """Trích xuất payload từ button click"""
        try:
            # Button payload thường được encode trong message attachments
            if hasattr(message, 'attachments') and message.attachments:
                for attachment in message.attachments:
                    if isinstance(attachment, dict) and 'payload' in attachment:
                        return attachment['payload']
            
            # Hoặc có thể trong message text dưới dạng JSON
            if hasattr(message, 'text') and message.text:
                import json
                try:
                    return json.loads(message.text)
                except json.JSONDecodeError:
                    pass
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting button payload: {str(e)}")
            return {}
    
    async def _handle_button_payload(self, user_id: str, payload: Dict[str, Any]) -> bool:
        """Xử lý payload từ button click"""
        try:
            action = payload.get('action')
            data = payload.get('data', {})
            
            logger.info(f"Button action '{action}' for user {user_id} with data: {data}")
            
            # Xử lý các actions khác nhau
            if action == "get_info":
                return await self._handle_get_info_action(user_id, data)
            elif action == "make_order":
                return await self._handle_make_order_action(user_id, data)
            elif action == "contact_support":
                return await self._handle_contact_support_action(user_id, data)
            else:
                logger.warning(f"Unknown button action: {action}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling button payload: {str(e)}")
            return False
    
    async def _handle_get_info_action(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Xử lý action lấy thông tin"""
        info_type = data.get('type', 'general')
        
        # Tạo response dựa trên loại thông tin được yêu cầu
        if info_type == 'contact':
            response = """📞 Thông tin liên hệ:

🏢 Công ty ABC
📧 Email: info@abc.com
☎️ Hotline: 1900-xxxx
🌐 Website: www.abc.com
📍 Địa chỉ: 123 ABC Street, City"""
        
        elif info_type == 'services':
            response = """🛍️ Dịch vụ của chúng tôi:

✅ Dịch vụ A
✅ Dịch vụ B  
✅ Dịch vụ C
✅ Hỗ trợ 24/7

Liên hệ để biết thêm chi tiết!"""
        
        else:
            response = "ℹ️ Thông tin tổng quan về dịch vụ của chúng tôi..."
        
        # TODO: Gửi response message
        logger.info(f"Info response for {user_id}: {response}")
        
        return True
    
    async def _handle_make_order_action(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Xử lý action đặt hàng"""
        product_id = data.get('product_id')
        
        logger.info(f"Order request for product {product_id} from user {user_id}")
        
        # Tạo order hoặc chuyển hướng đến form đặt hàng
        response = f"""📦 Đặt hàng sản phẩm #{product_id}

Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng.

Cần hỗ trợ thêm? Gửi /help"""
        
        # TODO: Gửi response và có thể tạo order record
        logger.info(f"Order response for {user_id}: {response}")
        
        return True
    
    async def _handle_contact_support_action(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Xử lý action liên hệ hỗ trợ"""
        issue_type = data.get('issue_type', 'general')
        
        logger.info(f"Support request type '{issue_type}' from user {user_id}")
        
        # Chuyển đến team support hoặc tạo ticket
        response = """🎧 Hỗ trợ khách hàng

Chúng tôi đã ghi nhận yêu cầu hỗ trợ của bạn.
Team hỗ trợ sẽ liên hệ với bạn trong vòng 24h.

Mã ticket: #SUP{timestamp}""".format(timestamp=int(datetime.now().timestamp()))
        
        # TODO: Tạo support ticket và gửi response
        logger.info(f"Support response for {user_id}: {response}")
        
        return True
    
    async def _save_follower_info(self, user_id: str, follower: Any, action: str) -> bool:
        """Lưu thông tin follower vào database"""
        try:
            # TODO: Implement database save
            # Ví dụ:
            # await db.followers.upsert({
            #     "user_id": user_id,
            #     "name": follower.name,
            #     "avatar": follower.avatar,
            #     "action": action,
            #     "timestamp": datetime.now()
            # })
            
            logger.info(f"Saved follower info: {user_id} - {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving follower info: {str(e)}")
            return False
    
    async def _save_user_submitted_info(self, user_id: str, info: Dict[str, Any]) -> bool:
        """Lưu thông tin do người dùng submit"""
        try:
            # TODO: Implement database save
            # await db.user_submissions.insert({
            #     "user_id": user_id,
            #     "info": info,
            #     "timestamp": datetime.now()
            # })
            
            logger.info(f"Saved user submitted info: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user submitted info: {str(e)}")
            return False
