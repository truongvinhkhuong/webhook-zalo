from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json

class ZaloUser(BaseModel):
    """Thông tin người dùng Zalo"""
    id: str
    name: Optional[str] = None
    avatar: Optional[str] = None

class ZaloMessage(BaseModel):
    """Tin nhắn từ Zalo"""
    msg_id: str
    text: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[int] = None  # Optional vì không phải lúc nào cũng có

class ZaloEvent(BaseModel):
    """Base class cho tất cả các sự kiện từ Zalo"""
    app_id: str
    event_name: str
    timestamp: str  # Zalo gửi timestamp dưới dạng string
    user_id_by_app: str
    
    class Config:
        extra = "allow"  # Cho phép các field bổ sung

class UserSendTextEvent(ZaloEvent):
    """Sự kiện người dùng gửi tin nhắn text"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class UserSendImageEvent(ZaloEvent):
    """Sự kiện người dùng gửi hình ảnh"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class UserSendFileEvent(ZaloEvent):
    """Sự kiện người dùng gửi file"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class UserSendStickerEvent(ZaloEvent):
    """Sự kiện người dùng gửi sticker"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class UserSendLocationEvent(ZaloEvent):
    """Sự kiện người dùng gửi vị trí"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class FollowOAEvent(ZaloEvent):
    """Sự kiện người dùng theo dõi OA"""
    follower: ZaloUser
    event_name: str = "follow"

class UnfollowOAEvent(ZaloEvent):
    """Sự kiện người dùng bỏ theo dõi OA"""
    follower: ZaloUser
    event_name: str = "unfollow"

class UserSubmitInfoEvent(ZaloEvent):
    """Sự kiện người dùng submit thông tin"""
    info: Dict[str, Any]
    sender: ZaloUser

class UserClickButtonEvent(ZaloEvent):
    """Sự kiện người dùng click button"""
    message: ZaloMessage
    sender: ZaloUser
    recipient: ZaloUser

class OAEvent(ZaloEvent):
    """Sự kiện liên quan đến OA"""
    oa: Dict[str, Any]

def parse_zalo_event(event_data: Dict[str, Any]) -> Optional[ZaloEvent]:
    """
    Parse raw event data từ Zalo thành ZaloEvent object tương ứng
    """
    try:
        event_name = event_data.get("event_name")
        
        if not event_name:
            return None
            
        # Mapping các event types
        event_classes = {
            "user_send_text": UserSendTextEvent,
            "user_send_image": UserSendImageEvent,
            "user_send_file": UserSendFileEvent,
            "user_send_sticker": UserSendStickerEvent,
            "user_send_location": UserSendLocationEvent,
            "follow": FollowOAEvent,
            "unfollow": UnfollowOAEvent,
            "user_submit_info": UserSubmitInfoEvent,
            "user_click_button": UserClickButtonEvent,
        }
        
        event_class = event_classes.get(event_name)
        
        if event_class:
            return event_class(**event_data)
        else:
            # Nếu không tìm thấy event class cụ thể, trả về ZaloEvent generic
            return ZaloEvent(**event_data)
            
    except Exception as e:
        print(f"Error parsing event: {e}")
        return None

class EventResponse(BaseModel):
    """Response model cho API endpoints"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
