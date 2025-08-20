#!/usr/bin/env python3
"""
Script test webhook server
"""

import requests
import json
import hashlib
import hmac
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = "http://localhost:8000/webhook"
SECRET_KEY = os.getenv("ZALO_SECRET_KEY", "test_secret")

def create_signature(payload: str) -> str:
    """Tạo signature cho test"""
    return hmac.new(
        SECRET_KEY.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_text_message():
    """Test text message event"""
    print("🧪 Testing text message event...")
    
    payload = {
        "app_id": "test_app_id",
        "event_name": "user_send_text",
        "timestamp": int(datetime.now().timestamp()),
        "user_id_by_app": "test_user_123",
        "message": {
            "msg_id": "test_msg_123",
            "text": "Hello from test!",
            "timestamp": int(datetime.now().timestamp())
        },
        "sender": {
            "id": "test_user_123",
            "name": "Test User",
            "avatar": "https://example.com/avatar.jpg"
        },
        "recipient": {
            "id": "test_oa_123",
            "name": "Test OA"
        }
    }
    
    payload_str = json.dumps(payload)
    signature = create_signature(payload_str)
    
    headers = {
        "Content-Type": "application/json",
        "X-Zalo-Signature": signature
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload_str, headers=headers)
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_follow_event():
    """Test follow event"""
    print("🧪 Testing follow event...")
    
    payload = {
        "app_id": "test_app_id",
        "event_name": "follow",
        "timestamp": int(datetime.now().timestamp()),
        "user_id_by_app": "test_user_456",
        "follower": {
            "id": "test_user_456",
            "name": "New Follower",
            "avatar": "https://example.com/avatar2.jpg"
        }
    }
    
    payload_str = json.dumps(payload)
    signature = create_signature(payload_str)
    
    headers = {
        "Content-Type": "application/json",
        "X-Zalo-Signature": signature
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload_str, headers=headers)
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print("🧪 Testing health check...")
    
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_webhook_verification():
    """Test webhook verification"""
    print("🧪 Testing webhook verification...")
    
    verify_token = os.getenv("ZALO_VERIFY_TOKEN", "test_verify_token")
    challenge = "test_challenge_123"
    
    try:
        response = requests.get(
            "http://localhost:8000/webhook",
            params={
                "hub_challenge": challenge,
                "hub_verify_token": verify_token
            }
        )
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting webhook tests...\n")
    
    tests = [
        test_health_check,
        test_webhook_verification,
        test_text_message,
        test_follow_event
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            failed += 1
        print("-" * 50)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check server logs.")

if __name__ == "__main__":
    main()
