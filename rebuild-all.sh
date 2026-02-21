cd ~/Desktop/imtiaz-mart-event-driven

# ═══════════════════════════════════════════════════════════════════
# Step 1: Update All Dockerfiles
# ═══════════════════════════════════════════════════════════════════

for service in product-service user-service order-service inventory-service payment-service; do
  case $service in
    user-service)       port=8000 ;;
    product-service)    port=8001 ;;
    payment-service)    port=8002 ;;
    order-service)      port=8003 ;;
    inventory-service)  port=8004 ;;
  esac

  cat > services/${service}/Dockerfile << EOF
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
EOF

  echo "✅ Updated ${service} Dockerfile"
done

# ═══════════════════════════════════════════════════════════════════
# Step 2: Update docker-compose.yml (Remove .venv Exclusions)
# ═══════════════════════════════════════════════════════════════════

cd infrastructure

# Remove /app/.venv lines
sed -i '/- \/app\/\.venv/d' docker-compose.yml

echo "✅ Removed .venv exclusions from docker-compose.yml"

# ═══════════════════════════════════════════════════════════════════
# Step 3: Stop Everything
# ═══════════════════════════════════════════════════════════════════

docker compose down --volumes --remove-orphans

echo "✅ Stopped all containers"

# ═══════════════════════════════════════════════════════════════════
# Step 4: Remove ALL Old Images
# ═══════════════════════════════════════════════════════════════════

echo "🗑️  Removing old images..."

# Remove service images
docker rmi -f imtiaz-mart/product-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/user-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/order-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/inventory-service:1.0.0 2>/dev/null || true
docker rmi -f imtiaz-mart/payment-service:1.0.0 2>/dev/null || true

# Remove dangling images
docker image prune -f

echo "✅ Old images removed"

# ═══════════════════════════════════════════════════════════════════
# Step 5: Remove All .venv Folders
# ═══════════════════════════════════════════════════════════════════

cd ..
sudo rm -rf services/product-service/.venv
sudo rm -rf services/user-service/.venv
sudo rm -rf services/order-service/.venv
sudo rm -rf services/inventory-service/.venv
sudo rm -rf services/payment-service/.venv

echo "✅ All .venv folders removed"

# ═══════════════════════════════════════════════════════════════════
# Step 6: Build New Images
# ═══════════════════════════════════════════════════════════════════

cd infrastructure

echo "🔨 Building new images (this will take a few minutes)..."

docker compose build --no-cache --pull

if [ $? -eq 0 ]; then
  echo "✅ All images built successfully!"
else
  echo "❌ Build failed!"
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════
# Step 7: Start All Services
# ═══════════════════════════════════════════════════════════════════

echo "🚀 Starting all services..."

docker compose up -d

echo "⏳ Waiting for services to start..."
sleep 20

# ═══════════════════════════════════════════════════════════════════
# Step 8: Check Status
# ═══════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 Container Status"
echo "═══════════════════════════════════════════════════════════════════"
docker compose ps

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🔍 Recent Logs"
echo "═══════════════════════════════════════════════════════════════════"
docker compose logs --tail=5

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🎉 Build Complete!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Check if all services are 'Up': docker compose ps"
echo "2. View logs: docker compose logs -f"
echo "3. Test endpoints:"
echo "   - Product:   curl http://localhost:8001/"
echo "   - User:      curl http://localhost:8000/"
echo "   - Payment:   curl http://localhost:8002/"
echo "   - Order:     curl http://localhost:8003/"
echo "   - Inventory: curl http://localhost:8004/"
echo ""
