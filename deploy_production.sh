#!/bin/bash

# Production Deployment Script for Zalo Webhook
# Run this script on your production server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Zalo Webhook to Production${NC}"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    exit 1
fi

# Configuration
PROJECT_DIR="/root/webhook-zalo"
NGINX_SITE="/etc/nginx/sites-available/zalo-webhook"
NGINX_ENABLED="/etc/nginx/sites-enabled/zalo-webhook"

echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose not found, installing...${NC}"
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}⚠️  Nginx not found, installing...${NC}"
    apt update
    apt install -y nginx
    systemctl enable nginx
    systemctl start nginx
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Navigate to project directory
echo -e "\n${YELLOW}📁 Setting up project directory...${NC}"
cd "$PROJECT_DIR"

# Create logs directory
mkdir -p logs

# Set proper permissions
chmod +x *.sh

echo -e "${GREEN}✅ Project directory setup completed${NC}"

# Setup Nginx configuration
echo -e "\n${YELLOW}🌐 Setting up Nginx configuration...${NC}"

# Copy nginx config
cp nginx-webhook.conf "$NGINX_SITE"

# Create symlink
if [ -L "$NGINX_ENABLED" ]; then
    rm "$NGINX_ENABLED"
fi
ln -s "$NGINX_SITE" "$NGINX_ENABLED"

# Test nginx config
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    systemctl reload nginx
else
    echo -e "${RED}❌ Nginx configuration is invalid${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Nginx setup completed${NC}"

# Setup SSL certificate (if not exists)
echo -e "\n${YELLOW}🔒 Setting up SSL certificate...${NC}"

DOMAIN="zalo.truongvinhkhuong.io.vn"
SSL_DIR="/etc/letsencrypt/live/$DOMAIN"

if [ ! -d "$SSL_DIR" ]; then
    echo -e "${YELLOW}⚠️  SSL certificate not found${NC}"
    echo "Please run: certbot --nginx -d $DOMAIN"
    echo "Or manually place SSL certificates in $SSL_DIR"
else
    echo -e "${GREEN}✅ SSL certificate found${NC}"
fi

# Build and start Docker services
echo -e "\n${YELLOW}🐳 Building and starting Docker services...${NC}"

# Stop existing containers
docker-compose down 2>/dev/null || true

# Build and start
docker-compose up -d --build

# Wait for service to be ready
echo -e "${YELLOW}⏳ Waiting for service to be ready...${NC}"
sleep 15

# Check service status
echo -e "\n${YELLOW}📊 Checking service status...${NC}"
docker-compose ps

# Test endpoints
echo -e "\n${YELLOW}🧪 Testing endpoints...${NC}"

# Test health check
echo "Testing health check endpoint:"
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Health check endpoint working${NC}"
else
    echo -e "${RED}❌ Health check endpoint failed${NC}"
fi

# Test dashboard
echo "Testing dashboard endpoint:"
if curl -s http://localhost:8001/ | grep -q "Zalo Webhook Dashboard"; then
    echo -e "${GREEN}✅ Dashboard endpoint working${NC}"
else
    echo -e "${RED}❌ Dashboard endpoint failed${NC}"
fi

echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"

# Final status
echo -e "\n${BLUE}📋 Final Status:${NC}"
echo "- Service: $(docker-compose ps --format 'table {{.Name}}\t{{.Status}}')"
echo "- Nginx: $(systemctl is-active nginx)"
echo "- Dashboard: https://$DOMAIN/"
echo "- Health Check: https://$DOMAIN/health"
echo "- Webhook: https://$DOMAIN/webhook"

echo -e "\n${YELLOW}📝 Next steps:${NC}"
echo "1. Configure your Zalo webhook URL: https://$DOMAIN/webhook"
echo "2. Set verify token and secret key in .env file"
echo "3. Test webhook with Zalo"
echo "4. Monitor logs: docker-compose logs -f"

echo -e "\n${GREEN}🚀 Your Zalo Webhook is now running!${NC}"
