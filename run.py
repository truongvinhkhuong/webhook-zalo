#!/usr/bin/env python3
"""
Script khởi chạy Zalo Webhook Server
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_environment():
    """Kiểm tra môi trường trước khi chạy"""
    print("🔍 Checking environment...")
    
    # Kiểm tra Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Kiểm tra .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        try:
            subprocess.run(["cp", ".env.example", ".env"], check=True)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your Zalo credentials")
        except subprocess.CalledProcessError:
            print("❌ Failed to create .env file")
            return False
    
    # Kiểm tra dependencies
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 Starting Zalo Webhook Server...")
    
    if not check_environment():
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, environment variables may not load")
    
    # Import và chạy app
    try:
        from config import settings
        import uvicorn
        
        print(f"🌐 Server will run on: http://0.0.0.0:{settings.PORT}")
        print(f"📊 Debug mode: {settings.DEBUG}")
        print(f"🔗 Webhook domain: {settings.WEBHOOK_DOMAIN}")
        print(f"📝 API docs will be available at: http://localhost:{settings.PORT}/docs")
        print("\n🎯 Webhook URL for Zalo: https://{}/webhook".format(settings.WEBHOOK_DOMAIN))
        print("\n⏳ Starting server...")
        
        # Chạy server
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
