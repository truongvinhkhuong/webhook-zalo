#!/bin/bash

echo "🔄 Restarting Zalo Webhook Service..."

# Stop the current containers
echo "⏹️  Stopping containers..."
docker-compose down

# Rebuild and start the service
echo "🔨 Rebuilding and starting service..."
docker-compose up -d --build

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test the endpoints
echo "🧪 Testing endpoints..."
echo "Testing health check endpoint:"
curl -s http://localhost:8001/health | jq . 2>/dev/null || curl -s http://localhost:8001/health

echo -e "\nTesting dashboard endpoint:"
curl -s http://localhost:8001/ | head -20

echo -e "\n✅ Service restart completed!"
echo "🌐 Dashboard available at: https://zalo.truongvinhkhuong.io.vn/"
echo "🔗 Health check: https://zalo.truongvinhkhuong.io.vn/health"
