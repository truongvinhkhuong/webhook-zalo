#!/bin/bash

# Script setup tự động cho Zalo Webhook Server

echo "🚀 Setting up Zalo Webhook Server..."

# Tạo virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
echo "⬇️  Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Tạo .env từ template
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Zalo credentials"
else
    echo "✅ .env file already exists"
fi

# Tạo thư mục logs
mkdir -p logs

# Cấp quyền execute cho scripts
chmod +x run.py
chmod +x test_webhook.py

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Zalo credentials"
echo "2. Run the server: python run.py"
echo "3. Test the webhook: python test_webhook.py"
echo ""
echo "🌐 Webhook URL: https://zalo.truongvinhkhuong.io.vn/webhook"
echo "📊 API Docs: http://localhost:8000/docs"
