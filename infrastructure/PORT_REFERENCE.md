# Imtiaz Mart - Complete Port Reference Guide

## 📋 Quick Overview

All ports are fully configurable via `.env` file. Change once, applies everywhere!

## 🎯 Port Allocation Strategy
```
Service Ports:     8000-8099  (HTTP APIs)
Dapr HTTP Ports:   3500-3599  (Dapr HTTP endpoints)
Dapr gRPC Ports:   50000-50099 (Dapr gRPC communication)
Dapr Metrics:      9090-9099  (Prometheus metrics)
Database Ports:    5436-5499  (PostgreSQL external access)
```

---

## 📊 Complete Services Port Map

### User Service (Authentication & User Management)

| Component | External Port | Internal Port | Environment Variable | Default |
|-----------|--------------|---------------|---------------------|---------|
| **HTTP API** | 8000 | 8000 | `USER_SERVICE_EXTERNAL_PORT` | 8000 |
| | | | `USER_SERVICE_INTERNAL_PORT` | 8000 |
| **Database** | 5436 | 5432 | `USER_DB_EXTERNAL_PORT` | 5436 |
| | | | `USER_DB_INTERNAL_PORT` | 5432 |
| **Dapr HTTP** | - | 3500 | `USER_DAPR_HTTP_PORT` | 3500 |
| **Dapr gRPC** | - | 50000 | `USER_DAPR_GRPC_PORT` | 50000 |
| **Dapr Metrics** | - | 9090 | `USER_DAPR_METRICS_PORT` | 9090 |

**Access URLs:**
```bash
API:    http://localhost:8000
Docs:   http://localhost:8000/docs
Health: http://localhost:8000/health
DB:     postgresql://imtiaz:password123@localhost:5436/user_db
```

---

### Product Service (Product Catalog Management)

| Component | External Port | Internal Port | Environment Variable | Default |
|-----------|--------------|---------------|---------------------|---------|
| **HTTP API** | 8001 | 8001 | `PRODUCT_SERVICE_EXTERNAL_PORT` | 8001 |
| | | | `PRODUCT_SERVICE_INTERNAL_PORT` | 8001 |
| **Database** | 5437 | 5432 | `PRODUCT_DB_EXTERNAL_PORT` | 5437 |
| | | | `PRODUCT_DB_INTERNAL_PORT` | 5432 |
| **Dapr HTTP** | - | 3501 | `PRODUCT_DAPR_HTTP_PORT` | 3501 |
| **Dapr gRPC** | - | 50001 | `PRODUCT_DAPR_GRPC_PORT` | 50001 |
| **Dapr Metrics** | - | 9091 | `PRODUCT_DAPR_METRICS_PORT` | 9091 |

**Access URLs:**
```bash
API:    http://localhost:8001
Docs:   http://localhost:8001/docs
Health: http://localhost:8001/health
DB:     postgresql://imtiaz:password123@localhost:5437/product_db
```

---

### Payment Service (PayFast & Stripe Integration)

| Component | External Port | Internal Port | Environment Variable | Default |
|-----------|--------------|---------------|---------------------|---------|
| **HTTP API** | 8002 | 8002 | `PAYMENT_SERVICE_EXTERNAL_PORT` | 8002 |
| | | | `PAYMENT_SERVICE_INTERNAL_PORT` | 8002 |
| **Database** | 5440 | 5432 | `PAYMENT_DB_EXTERNAL_PORT` | 5440 |
| | | | `PAYMENT_DB_INTERNAL_PORT` | 5432 |
| **Dapr HTTP** | - | 3502 | `PAYMENT_DAPR_HTTP_PORT` | 3502 |
| **Dapr gRPC** | - | 50002 | `PAYMENT_DAPR_GRPC_PORT` | 50002 |
| **Dapr Metrics** | - | 9092 | `PAYMENT_DAPR_METRICS_PORT` | 9092 |

**Access URLs:**
```bash
API:    http://localhost:8002
Docs:   http://localhost:8002/docs
Health: http://localhost:8002/health
DB:     postgresql://imtiaz:password123@localhost:5440/payment_db
```

---

### Order Service (Order Management & Processing)

| Component | External Port | Internal Port | Environment Variable | Default |
|-----------|--------------|---------------|---------------------|---------|
| **HTTP API** | 8003 | 8003 | `ORDER_SERVICE_EXTERNAL_PORT` | 8003 |
| | | | `ORDER_SERVICE_INTERNAL_PORT` | 8003 |
| **Database** | 5438 | 5432 | `ORDER_DB_EXTERNAL_PORT` | 5438 |
| | | | `ORDER_DB_INTERNAL_PORT` | 5432 |
| **Dapr HTTP** | - | 3503 | `ORDER_DAPR_HTTP_PORT` | 3503 |
| **Dapr gRPC** | - | 50003 | `ORDER_DAPR_GRPC_PORT` | 50003 |
| **Dapr Metrics** | - | 9093 | `ORDER_DAPR_METRICS_PORT` | 9093 |

**Access URLs:**
```bash
API:    http://localhost:8003
Docs:   http://localhost:8003/docs
Health: http://localhost:8003/health
DB:     postgresql://imtiaz:password123@localhost:5438/order_db
```

---

### Inventory Service (Stock Management)

| Component | External Port | Internal Port | Environment Variable | Default |
|-----------|--------------|---------------|---------------------|---------|
| **HTTP API** | 8004 | 8004 | `INVENTORY_SERVICE_EXTERNAL_PORT` | 8004 |
| | | | `INVENTORY_SERVICE_INTERNAL_PORT` | 8004 |
| **Database** | 5439 | 5432 | `INVENTORY_DB_EXTERNAL_PORT` | 5439 |
| | | | `INVENTORY_DB_INTERNAL_PORT` | 5432 |
| **Dapr HTTP** | - | 3504 | `INVENTORY_DAPR_HTTP_PORT` | 3504 |
| **Dapr gRPC** | - | 50004 | `INVENTORY_DAPR_GRPC_PORT` | 50004 |
| **Dapr Metrics** | - | 9094 | `INVENTORY_DAPR_METRICS_PORT` | 9094 |

**Access URLs:**
```bash
API:    http://localhost:8004
Docs:   http://localhost:8004/docs
Health: http://localhost:8004/health
DB:     postgresql://imtiaz:password123@localhost:5439/inventory_db
```

---

## 🏗️ Infrastructure Services

### Kafka (Event Streaming)

| Component | Port | Environment Variable | Default |
|-----------|------|---------------------|---------|
| External | 9092 | `KAFKA_EXTERNAL_PORT` | 9092 |
| Internal | 29092 | `KAFKA_INTERNAL_PORT` | 29092 |

**Access:**
```bash
kafka://localhost:9092
```

### Zookeeper (Kafka Coordination)

| Component | Port | Environment Variable | Default |
|-----------|------|---------------------|---------|
| Client | 2181 | `ZOOKEEPER_PORT` | 2181 |

---

## 🔄 Port Pattern Explanation

### External vs Internal Ports
```
┌──────────────┐         ┌──────────────────┐
│ Your Laptop  │         │ Docker Container │
│ (Host)       │         │                  │
│              │         │                  │
│ localhost:   │  ────>  │  container:      │
│   8002       │         │     8002         │
│              │         │                  │
│ External Port│         │  Internal Port   │
└──────────────┘         └──────────────────┘
```

**Why separate?**
- **External**: What you access from your machine (configurable to avoid conflicts)
- **Internal**: What the app listens on inside container (usually keep as default)

---

## 🎛️ How to Change Ports

### Example 1: Change Payment Service to Port 9002

**Edit `.env`:**
```bash
PAYMENT_SERVICE_EXTERNAL_PORT=9002
PAYMENT_SERVICE_INTERNAL_PORT=9002  # Usually keep same
```

**Restart:**
```bash
docker-compose restart payment-service payment-service-dapr
```

**Access:**
```bash
curl http://localhost:9002/health  # Now on port 9002!
```

### Example 2: Run Payment on Port 80 (Requires Sudo)

**Edit `.env`:**
```bash
PAYMENT_SERVICE_EXTERNAL_PORT=80     # External accessible on :80
PAYMENT_SERVICE_INTERNAL_PORT=8002   # Internal still 8002
```

**Why?** You want users to access on standard HTTP port 80, but app runs on 8002 internally.

### Example 3: Change All Databases to 5500+ Range

**Edit `.env`:**
```bash
USER_DB_EXTERNAL_PORT=5500
PRODUCT_DB_EXTERNAL_PORT=5501
PAYMENT_DB_EXTERNAL_PORT=5502
ORDER_DB_EXTERNAL_PORT=5503
INVENTORY_DB_EXTERNAL_PORT=5504
```

---

## 📝 Environment-Specific Configurations

### Development (.env or .env.dev)
```bash
# Use default ports
USER_SERVICE_EXTERNAL_PORT=8000
PRODUCT_SERVICE_EXTERNAL_PORT=8001
PAYMENT_SERVICE_EXTERNAL_PORT=8002
# etc...
```

### Staging (.env.staging)
```bash
# Different ports to avoid conflicts
USER_SERVICE_EXTERNAL_PORT=9000
PRODUCT_SERVICE_EXTERNAL_PORT=9001
PAYMENT_SERVICE_EXTERNAL_PORT=9002
# etc...
```

### Production (.env.prod)
```bash
# Standard ports behind reverse proxy
USER_SERVICE_EXTERNAL_PORT=8080
PRODUCT_SERVICE_EXTERNAL_PORT=8081
PAYMENT_SERVICE_EXTERNAL_PORT=8082
# etc...
```

**Run with specific environment:**
```bash
docker-compose --env-file .env.staging up -d
```

---

## 🧪 Testing & Verification

### Health Check All Services
```bash
#!/bin/bash
# health-check-all.sh

services=(
  "user:8000"
  "product:8001"
  "payment:8002"
  "order:8003"
  "inventory:8004"
)

for service in "${services[@]}"; do
  IFS=':' read -r name port <<< "$service"
  echo -n "Checking ${name} service... "
  if curl -s "http://localhost:${port}/health" > /dev/null; then
    echo "✅ Healthy"
  else
    echo "❌ Down"
  fi
done
```

### Check Database Connections
```bash
# User DB
psql -h localhost -p 5436 -U imtiaz -d user_db

# Product DB
psql -h localhost -p 5437 -U imtiaz -d product_db

# Payment DB
psql -h localhost -p 5440 -U imtiaz -d payment_db

# Order DB
psql -h localhost -p 5438 -U imtiaz -d order_db

# Inventory DB
psql -h localhost -p 5439 -U imtiaz -d inventory_db
```

### Check Dapr Sidecars
```bash
# Check all Dapr sidecars are running
docker ps | grep dapr

# Check specific Dapr health
curl http://localhost:3502/v1.0/healthz  # Payment Dapr
curl http://localhost:3501/v1.0/healthz  # Product Dapr
```

---

## 🚨 Common Port Conflicts

### Conflict: Port Already in Use
```bash
Error: bind: address already in use
```

**Solution 1: Find what's using the port**
```bash
# Linux/Mac
lsof -i :8002
sudo netstat -tulpn | grep 8002

# Windows
netstat -ano | findstr :8002
```

**Solution 2: Change the port in .env**
```bash
PAYMENT_SERVICE_EXTERNAL_PORT=8102  # Use different port
```

### Conflict: Multiple Databases on Same Port

**Bad:**
```bash
USER_DB_EXTERNAL_PORT=5432
PRODUCT_DB_EXTERNAL_PORT=5432  # ❌ Conflict!
```

**Good:**
```bash
USER_DB_EXTERNAL_PORT=5436     # ✅ Unique
PRODUCT_DB_EXTERNAL_PORT=5437  # ✅ Unique
```

---

## 📚 Quick Reference Commands
```bash
# View all ports in use
docker-compose ps

# View specific service ports
docker port imtiaz-payment-service

# Test all services
for port in 8000 8001 8002 8003 8004; do
  curl -s http://localhost:$port/health && echo " - Port $port OK"
done

# Restart service after port change
docker-compose restart <service-name>

# Validate docker-compose configuration
docker-compose config

# View environment variables
docker-compose config | grep PORT
```

---

## 🔐 Security Notes

1. **Internal Ports**: Not exposed to host, only accessible within Docker network
2. **External Ports**: Exposed to host, accessible via localhost
3. **Production**: Use reverse proxy (nginx/traefik) and don't expose databases externally
4. **Firewall**: In production, only expose necessary ports through firewall

---

## 📖 Additional Resources

- **Docker Compose Networking**: https://docs.docker.com/compose/networking/
- **Port Mapping**: https://docs.docker.com/config/containers/container-networking/
- **Dapr Documentation**: https://docs.dapr.io/
- **PostgreSQL Ports**: https://www.postgresql.org/docs/current/runtime-config-connection.html

---

## 🎯 Summary

✅ **All ports configurable via `.env`**
✅ **Single source of truth**
✅ **Environment-specific configurations**
✅ **No hardcoded values in docker-compose.yml**
✅ **Easy to scale and manage**

**Remember:** Change `.env` → Restart service → Port updated! 🚀

---

*Last Updated: 2025-12-27*
*Maintained by: DevOps Team*
