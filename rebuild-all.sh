#!/bin/bash

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Complete Rebuild - All Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

# ═══════════════════════════════════════════════════════════════════
# Step 1: Update All Dockerfiles
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 1: Updating Dockerfiles...${NC}"

for service in product-service user-service order-service inventory-service payment-service; do
  case $service in
    user-service)       port=8000 ;;
    product-service)    port=8001 ;;
    payment-service)    port=8002 ;;
    order-service)      port=8003 ;;
    inventory-service)  port=8004 ;;
  esac

  cat > services/${service}/Dockerfile << DOCKERFILE
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy everything
COPY . .

# Install dependencies
RUN uv sync

EXPOSE ${port}

# Use uv run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${port}", "--reload"]
DOCKERFILE

  echo -e "${GREEN}✅ Updated ${service}${NC}"
done

# ═══════════════════════════════════════════════════════════════════
# Step 2: Update docker-compose.yml
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 2: Cleaning docker-compose.yml...${NC}"

cd infrastructure
sed -i '/- \/app\/\.venv/d' docker-compose.yml
echo -e "${GREEN}✅ Removed .venv exclusions${NC}"

# ═══════════════════════════════════════════════════════════════════
# Step 3: Stop Everything
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 3: Stopping containers...${NC}"
docker compose down --volumes --remove-orphans
echo -e "${GREEN}✅ Stopped${NC}"

# ═══════════════════════════════════════════════════════════════════
# Step 4: Remove Old Images
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 4: Removing old images...${NC}"

docker rmi -f imtiaz-mart/product-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/user-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/order-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/inventory-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/payment-service:1.0.0 2>/dev/null || true

docker image prune -f

echo -e "${GREEN}✅ Old images removed${NC}"

# ═══════════════════════════════════════════════════════════════════
# Step 5: Remove .venv
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 5: Removing .venv folders...${NC}"

cd ..
sudo rm -rf services/product-service/.venv
sudo rm -rf services/user-service/.venv
sudo rm -rf services/order-service/.venv
sudo rm -rf services/inventory-service/.venv
sudo rm -rf services/payment-service/.venv

echo -e "${GREEN}✅ .venv folders removed${NC}"

# ═══════════════════════════════════════════════════════════════════
# Step 6: Build
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 6: Building new images (this takes time)...${NC}"

cd infrastructure
docker compose build --no-cache --pull

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Build successful!${NC}"
else
  echo -e "${RED}❌ Build failed!${NC}"
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════
# Step 7: Start Services
# ═══════════════════════════════════════════════════════════════════

echo -e "${YELLOW}Step 7: Starting services...${NC}"

docker compose up -d

echo -e "${YELLOW}Waiting 20 seconds for services to start...${NC}"
sleep 20

# ═══════════════════════════════════════════════════════════════════
# Step 8: Show Status
# ═══════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Container Status${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
docker compose ps

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Recent Logs${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
docker compose logs --tail=3

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Rebuild Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  • Check status: docker compose ps"
echo "  • View logs: docker compose logs -f"
echo "  • Test endpoints:"
echo "      curl http://localhost:8001/  # product"
echo "      curl http://localhost:8000/  # user"
echo "      curl http://localhost:8002/  # payment"
echo "      curl http://localhost:8003/  # order"
echo "      curl http://localhost:8004/  # inventory"
echo ""
