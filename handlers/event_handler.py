import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import asyncio

from models.zalo_events import (
    ZaloEvent, UserSendTextEvent, UserSendImageEvent, UserSendFileEvent,
    UserSendStickerEvent, UserSendLocationEvent, FollowOAEvent, UnfollowOAEvent,
    UserSubmitInfoEvent, UserClickButtonEvent
)
from handlers.message_handler import MessageHandler
from handlers.user_action_handler import UserActionHandler

logger = logging.getLogger(__name__)

class EventHandler:
    """
    Main event handler để xử lý tất cả các sự kiện từ Zalo
    """
    
    def __init__(self):
        self.message_handler = MessageHandler()
        self.user_action_handler = UserActionHandler()
        
        # Lưu trữ events gần đây để debug (trong memory)
        self.recent_events: deque = deque(maxlen=100)
        
        # Statistics
        self.event_stats = {}
        
    async def handle_event(self, event: ZaloEvent) -> bool:
        """
        Xử lý event từ Zalo
        
        Args:
            event: ZaloEvent object
            
        Returns:
            bool: True nếu xử lý thành công
        """
        try:
            # Lưu event vào recent events
            self._store_recent_event(event)
            
            # Cập nhật statistics
            self._update_stats(event.event_name)
            
            # Log event
            logger.info(f"Handling event: {event.event_name} from user: {event.user_id_by_app}")
            
            # Route event đến handler tương ứng
            success = await self._route_event(event)
            
            if success:
                logger.info(f"Successfully processed event: {event.event_name}")
            else:
                logger.warning(f"Failed to process event: {event.event_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error handling event {event.event_name}: {str(e)}")
            return False
    
    async def _route_event(self, event: ZaloEvent) -> bool:
        """Route event đến handler phù hợp"""
        
        # Message events
        if isinstance(event, (UserSendTextEvent, UserSendImageEvent, UserSendFileEvent, 
                            UserSendStickerEvent, UserSendLocationEvent)):
            handled = await self.message_handler.handle_message_event(event)
            try:
                # Ghi riêng sự kiện ảnh vào DB nếu có
                if isinstance(event, UserSendImageEvent):
                    from app import AsyncSessionLocal, ImageMessageEvent
                    async with AsyncSessionLocal() as session:
                        await self._persist_image_event(session, event)
                return handled
            except Exception as e:
                logger.error(f"DB persist error: {e}")
                return handled
        
        # User action events
        elif isinstance(event, (FollowOAEvent, UnfollowOAEvent, UserSubmitInfoEvent, 
                              UserClickButtonEvent)):
            return await self.user_action_handler.handle_user_action_event(event)
        
        # Generic event handler
        else:
            return await self._handle_generic_event(event)

    async def _persist_image_event(self, session, event: "UserSendImageEvent") -> None:
        attachments = event.message.attachments or []
        record = ImageMessageEvent(
            app_id=event.app_id,
            user_id_by_app=event.user_id_by_app,
            sender_id=event.sender.id if getattr(event, "sender", None) else "",
            recipient_id=event.recipient.id if getattr(event, "recipient", None) else "",
            event_name=event.event_name,
            timestamp=int(event.timestamp),
            msg_id=event.message.msg_id if event.message else None,
            text=event.message.text if event.message else None,
            attachments={"attachments": attachments},
        )
        session.add(record)
        await session.commit()
    
    async def _handle_generic_event(self, event: ZaloEvent) -> bool:
        """Xử lý các events chưa được định nghĩa cụ thể"""
        logger.info(f"Handling generic event: {event.event_name}")
        logger.debug(f"Event data: {event.model_dump()}")
        
        # Ở đây bạn có thể thêm logic xử lý chung
        # Ví dụ: lưu vào database, gửi notification, etc.
        
        return True
    
    def _store_recent_event(self, event: ZaloEvent):
        """Lưu trữ event gần đây"""
        event_record = {
            "timestamp": datetime.now(),
            "event_name": event.event_name,
            "user_id": event.user_id_by_app,
            "app_id": event.app_id,
            "data": event.model_dump()
        }
        self.recent_events.append(event_record)
    
    def _update_stats(self, event_name: str):
        """Cập nhật statistics"""
        if event_name not in self.event_stats:
            self.event_stats[event_name] = {
                "count": 0,
                "last_received": None
            }
        
        self.event_stats[event_name]["count"] += 1
        self.event_stats[event_name]["last_received"] = datetime.now()
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy danh sách events gần đây"""
        events = list(self.recent_events)[-limit:]
        
        # Convert datetime to string để serialize JSON
        for event in events:
            event["timestamp"] = event["timestamp"].isoformat()
            if event.get("data", {}).get("timestamp"):
                # Convert unix timestamp to readable format
                event["data"]["timestamp_readable"] = datetime.fromtimestamp(
                    event["data"]["timestamp"]
                ).isoformat()
        
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê events"""
        stats = {}
        for event_name, data in self.event_stats.items():
            stats[event_name] = {
                "count": data["count"],
                "last_received": data["last_received"].isoformat() if data["last_received"] else None
            }
        
        return {
            "total_events": len(self.recent_events),
            "event_types": stats,
            "uptime": datetime.now().isoformat()
        }
