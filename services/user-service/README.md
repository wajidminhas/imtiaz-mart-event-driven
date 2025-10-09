# User Service

A microservice for managing user authentication, registration, and profile management in the Imtiaz Marketplace platform.

## Features

- ✅ User registration with validation
- ✅ JWT-based authentication
- ✅ Password hashing and security
- ✅ User profile management
- ✅ Account soft deletion with recovery period
- ✅ Username reservation for deleted accounts
- ✅ Event-driven architecture with Dapr
- ✅ PostgreSQL database integration
- ✅ RESTful API with FastAPI

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Message Broker**: Dapr + Kafka
- **Containerization**: Docker
- **Package Manager**: uv

## Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Docker & Docker Compose
- Dapr CLI (for local development)

## Project Structure

```
user-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database      	        # Database connection
|   |	connections.py
│   ├── models/
│   │   └── user.py             # User database model
│   ├── routers/
│   │   └── users.py            # User endpoints
│   ├── crud/
│   │   └── user.py             # Database operations
│   └── events/
│       └── publisher.py        # Event publishing with Dapr
├── .env                        # Environment variables (local)
├── .env.docker                 # Environment variables (Docker)
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Environment Variables

### Local Development (.env)
```env
# Database
POSTGRES_USER=postgres			change into localhost in local development
POSTGRES_PASSWORD=password		change your credentials here
DB_HOST=localhost
DB_PORT=5436
POSTGRES_DB=userdb
DATABASE_URL=postgresql://postgres:password@localhost:5436/userdb

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=User Service
APP_VERSION=1.0.0
DEBUG=True

# Dapr
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
PUBSUB_NAME=order-pubsub
```

### Docker Environment
The docker-compose.yml overrides these for containerized deployment:
- `DB_HOST=postgres` (service name)
- `DB_PORT=5432` (internal container port)

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd services/user-service
```

2. **Install dependencies with uv**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start PostgreSQL (via Docker)**
```bash
cd ../../infrastructure
docker-compose up -d postgres
```

5. **Run database migrations**
```bash
# TODO: Add Alembic migrations
```

6. **Start the service**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# From the infrastructure directory
cd infrastructure
docker-compose up -d user-service
```

## API Endpoints

### Health Check
```
GET /health
```

### Authentication

#### Register User
```http
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response**: `201 Created`
```json
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2025-10-08T12:00:00Z"
}
```

#### Login
```http
POST /api/v1/users/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Management

#### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

#### Update Profile
```http
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith"
}
```

#### Delete Account (Soft Delete)
```http
DELETE /api/v1/users/me
Authorization: Bearer <token>
```

**Note**: Username is reserved for 30 days for account recovery.

## Business Logic

### Username Reservation
When a user deletes their account:
- Account is soft-deleted (`is_active=false`)
- Username is reserved for 30 days
- During this period, the username cannot be registered by others
- After 30 days, the username becomes available again

### Password Security
- Passwords are hashed using bcrypt
- Minimum password requirements enforced
- Plain text passwords never stored

### Event Publishing
The service publishes events via Dapr to Kafka:
- `user.registered` - When a new user registers
- `user.updated` - When user profile is updated
- `user.deleted` - When user account is deleted

## Development

### Run Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black app/
uv run isort app/
```

### Type Checking
```bash
uv run mypy app/
```

### Linting
```bash
uv run ruff check app/
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);
```

## Monitoring & Logging

- Application logs are written to stdout
- Health check endpoint: `/health`
- Metrics endpoint: `/metrics` (TODO)

## Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- CORS configuration
- SQL injection prevention via SQLModel
- Input validation via Pydantic

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
psql -h localhost -p 5436 -U postgres -d userdb
```

### Service Won't Start
```bash
# Check logs
docker-compose logs user-service

# Rebuild container
docker-compose up --build -d user-service
```

### Dapr Issues
```bash
# Check Dapr sidecar
docker-compose logs user-service-dapr

# Verify Dapr is running
dapr list
```

## Performance Considerations

- Database connection pooling enabled
- Indexes on username and email columns
- Background tasks for event publishing
- Async/await for I/O operations

## Future Enhancements

- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting
- [ ] User roles and permissions
- [ ] Profile picture upload
- [ ] Account recovery process
- [ ] Audit logging
- [ ] Advanced search and filtering

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

[Your License Here]

## Contact

- **Project Maintainer**: [Wajid Shabbir]
- **Email**: [shanitent667@gmail.com]


## Related Services

- Product Service
- Order Service
- Inventory Service
- Payment Service
- Notification Service

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`