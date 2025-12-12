cd ~/Desktop/imtiaz-mart-event-driven

cat > README.md << 'EOF'
# Imtiaz Mart - Event-Driven Microservices

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)

Complete e-commerce platform built with event-driven microservices architecture.

## 🏗️ Architecture
```mermaid
graph TB
    subgraph Kong["🔒 Kong API Gateway"]
        K[Authentication | Rate Limiting | Routing]
    end
    
    subgraph Services["🚀 Microservices"]
        U[👤 User Service<br/>Port 8000]
        P[📦 Product Service<br/>Port 8001]
        O[🛒 Order Service<br/>Port 8003]
        I[📊 Inventory Service<br/>Port 8004]
        Pay[💳 Payment Service<br/>Port 8005]
    end
    
    subgraph EventBus["📨 Event Bus"]
        Kafka[Apache Kafka<br/>• product.created<br/>• order.created<br/>• payment.success<br/>• inventory.low-stock]
    end
    
    subgraph Consumers["📢 Consumer Services"]
        N[📧 Notification<br/>SendGrid | Twilio]
        A[📈 Analytics]
    end
    
    Kong --> U & P & O & I & Pay
    U & P & O & I & Pay -.event.-> Kafka
    Kafka -.consume.-> N & A & I & O
    
    style Kong fill:#dae8fc,stroke:#6c8ebf
    style Kafka fill:#fff2cc,stroke:#d6b656
    style N fill:#e1d5e7,stroke:#9673a6
    style A fill:#e1d5e7,stroke:#9673a6
```

## ✨ Features

- **Event-Driven Architecture** - Asynchronous communication via Kafka
- **Microservices** - Independent, scalable services
- **Test-Driven Development** - 95%+ test coverage
- **Docker Compose** - One-command deployment
- **Dapr Integration** - Service mesh for resilience
- **API Gateway** - Kong for centralized routing

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLModel |
| **Message Broker** | Apache Kafka |
| **Service Mesh** | Dapr |
| **Containerization** | Docker Compose |
| **API Gateway** | Kong |
| **Testing** | Pytest (TDD/BDD) |
| **Cloud** | Azure Container Apps |

## 📊 Services Overview

### 1. **User Service** (Port 8000)
- User registration/login
- JWT authentication
- Profile management

### 2. **Product Service** (Port 8001)
- Product CRUD operations
- Catalog management
- **Events Published:** `product.created`, `product.updated`

### 3. **Order Service** (Port 8003)
- Order creation & tracking
- Order cancellation
- **Events Published:** `order.created`, `order.cancelled`
- **Events Consumed:** `product.*`, `payment.success`

### 4. **Inventory Service** (Port 8004)
- Stock management
- Movement tracking (audit trail)
- Low stock alerts
- **Events Published:** `inventory.low-stock`, `inventory.out-of-stock`
- **Events Consumed:** `product.created`, `order.created`

### 5. **Payment Service** (Port 8005)
- Payment processing (PayFast + Stripe)
- Refund handling
- **Events Published:** `payment.success`, `payment.failed`

### 6. **Notification Service** (Port 8006)
- Email notifications (SendGrid)
- SMS alerts (Twilio)
- **Events Consumed:** ALL events

## 🚀 Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd imtiaz-mart-event-driven

# Start all services
cd infrastructure
docker compose up -d

# Check services
docker compose ps

# Access services
# Product API: http://localhost:8001/docs
# Order API: http://localhost:8003/docs
# Inventory API: http://localhost:8004/docs
```

## 🧪 Running Tests
```bash
# Run all tests
cd services/product-service
uv run pytest tests/ -v

cd ../order-service
uv run pytest tests/ -v

cd ../inventory-service
uv run pytest tests/ -v
```

## 📁 Project Structure
```
imtiaz-mart-event-driven/
├── infrastructure/
│   ├── docker-compose.yml
│   ├── dapr/
│   │   ├── components/
│   │   └── config.yaml
│   └── .env
├── services/
│   ├── product-service/
│   ├── order-service/
│   ├── inventory-service/
│   ├── user-service/
│   ├── payment-service/
│   └── notification-service/
├── shared/
└── README.md
```

## 🔄 Event Flow Example

### Creating an Order:

1. **Client** → POST `/orders` → **Order Service**
2. **Order Service** → Publishes `order.created` → **Kafka**
3. **Kafka** → Distributes event to:
   - **Inventory Service**: Reduces stock
   - **Payment Service**: Processes payment
   - **Notification Service**: Sends confirmation email
4. **Payment Service** → Publishes `payment.success` → **Kafka**
5. **Order Service** → Updates order status to "confirmed"

## 🎯 API Documentation

Each service provides interactive Swagger documentation:

- User Service: http://localhost:8000/docs
- Product Service: http://localhost:8001/docs
- Order Service: http://localhost:8003/docs
- Inventory Service: http://localhost:8004/docs

## 🔒 Environment Variables

Create `.env` file in `infrastructure/`:
```bash
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
PRODUCT_DB_NAME=product_db
ORDER_DB_NAME=order_db
INVENTORY_DB_NAME=inventory_db
```

## 📈 Test Coverage

| Service | Tests | Coverage |
|---------|-------|----------|
| Product Service | 28/28 ✅ | 95%+ |
| Order Service | 25/25 ✅ | 95%+ |
| Inventory Service | 26/26 ✅ | 95%+ |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Write tests (TDD approach)
4. Commit changes
5. Push and create PR

## 📝 License

MIT License

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername]
- LinkedIn: [Your Profile]
- Email: your.email@example.com

---

⭐ **Star this repo if you find it helpful!**
EOF