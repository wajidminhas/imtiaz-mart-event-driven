
# Imtiaz Marketplace Backend

A microservices-based e-commerce platform built with FastAPI, PostgreSQL, Kafka, and Dapr.

## Architecture

Event-driven microservices architecture with:
- 5 independent services
- PostgreSQL for data persistence
- Kafka for event streaming
- Dapr for service communication
- Docker for containerization

## Services

| Service | Description | Port | Documentation |
|---------|-------------|------|---------------|
| [User Service](./services/user-service/README.md) | Authentication & user management | 8000 | [API Docs](http://localhost:8000/docs) |
| [Product Service](./services/product-service/README.md) | Product catalog management | 8001 | [API Docs](http://localhost:8001/docs) |
| [Order Service](./services/order-service/README.md) | Order processing & management | 8002 | [API Docs](http://localhost:8002/docs) |
| [Inventory Service](./services/inventory-service/README.md) | Stock & inventory management | 8003 | [API Docs](http://localhost:8003/docs) |
| [Payment Service](./services/payment-service/README.md) | Payment processing | 8004 | [API Docs](http://localhost:8004/docs) |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- PostgreSQL 15+

### Start All Services
```bash
cd infrastructure
docker-compose up -d
