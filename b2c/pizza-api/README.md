# Pizza Shack REST API

A well-structured FastAPI-based backend service for Pizza Shack application following modern Python development patterns. This refactored implementation provides a clean architecture with proper separation of concerns, modular design, and comprehensive JWT token handling.

## 🏗️ Project Structure

The refactored codebase follows industry best practices with a modular architecture:

```
pizza-api/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization & middleware
│   ├── routes.py                  # API endpoints organized by functionality
│   ├── schemas.py                 # Pydantic models for request/response validation
│   ├── database.py                # Database models & configuration
│   └── dependencies.py            # Dependency injection (auth, DB sessions)
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment configuration template
├── Dockerfile                     # Container configuration
├── openapi.yaml                   # OpenAPI/Swagger specification
└── db/                           # Database scripts
    ├── create_tables.sql
    ├── seed_data.sql
    └── sample_orders.sql
```

### File Responsibilities

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app setup, middleware, exception handlers |
| `app/routes.py` | API endpoints with proper route organization |
| `app/schemas.py` | Pydantic models for validation & serialization |
| `app/database.py` | SQLAlchemy models & database initialization |
| `app/dependencies.py` | Dependency injection for auth & database |
| `main.py` | Application entry point for deployment |

## 🚀 Features

### Architecture Improvements

- **Modular Structure**: Clean separation following FastAPI best practices
- **Pydantic Validation**: Strong typing with automatic input validation
- **Dependency Injection**: Proper auth and database session handling
- **Error Handling**: Consistent error responses with proper status codes
- **Route Organization**: Endpoints grouped logically with prefixes

### Authentication & Authorization

- **JWT Token Processing**: Secure token decoding for user context
- **OBO Token Support**: On-Behalf-Of tokens for AI agent interactions
- **Scope-Based Auth**: Extensible authorization framework
- **External Validation**: Token validation handled by WSO2 Choreo

### Database Integration

- **SQLAlchemy ORM**: Modern database abstraction
- **Multiple Database Support**: PostgreSQL for production, SQLite for development
- **Auto-initialization**: Database tables and seed data created on startup
- **Migration Support**: Ready for Alembic database migrations

## 📋 API Endpoints

### Public Endpoints (No Authentication)

```http
GET /                              # API information
GET /health                        # Health check
GET /api/menu                      # Get pizza menu with filtering
```

### Authenticated Endpoints (JWT + Scope Required)

```http
GET /api/token-info                # Debug token information (any valid token)
GET /api/system/status             # System status (any valid token)
POST /api/orders                   # Create new order (requires order:write)
GET /api/orders                    # Get user's orders (requires order:read)
GET /api/orders/{order_id}         # Get specific order (requires order:read)
# Admin endpoints removed - not used by pizza-shack frontend
```

## 🔑 Authentication Architecture

### Token Validation Pattern

Following the hotel API reference architecture, the Pizza API implements **scope-based authentication** with **external validation**:

```python
# Token validation with scope checking
@api_router.post("/orders", response_model=OrderResponse)
def create_order(
    request: Request,
    order_request: CreateOrderRequest,
    token_info: TokenInfo = Depends(validate_token),  # Validates token format
    db: Session = Depends(get_db)
):
    log_request_details(request, token_info)
    # Business logic here
```

### JWT Token Processing

The system handles two types of tokens:

**User Tokens (Direct Access):**
```json
{
  "sub": "user123",
  "aud": "pizza-app",
  "scope": "order:read order:write"
}
```

**OBO Tokens (Agent Acting for User):**
```json
{
  "sub": "user123",
  "act": {
    "sub": "pizza-ai-agent"
  },
  "aud": "pizza-app",
  "scope": "order:read order:write"
}
```

### Scope-Based Authorization

The API implements **complete scope-based authorization** similar to the hotel API pattern:

```python
# Scope validation with SecurityScopes
@api_router.post("/orders", response_model=OrderResponse)
def create_order(
    request: Request,
    order_request: CreateOrderRequest,
    token_data: TokenData = Security(validate_token, scopes=["order:write"]),
    db: Session = Depends(get_db)
):
    # Only users with order:write scope can create orders
```

**Available Scopes:**
- `order:read` - Read access to user orders
- `order:write` - Create and modify orders

**Scope Validation:**
- Tokens must contain **ALL** required scopes for an endpoint
- 403 Forbidden returned if insufficient permissions
- Scopes extracted from JWT `scope` claim (space-separated string or array)

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (optional - defaults to SQLite)
- WSO2 Asgardeo account

### Quick Start

1. **Clone and setup:**

```bash
cd pizza-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start the server:**

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

4. **Access the API:**

- API Server: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗄️ Database Configuration

### Environment Variables

```bash
# SQLite (Default for local development)
DATABASE_URL=sqlite:///./pizza_shack.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://username:password@localhost:5432/pizzashack

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CORS_METHODS=*
CORS_HEADERS=*
CORS_CREDENTIALS=true
```

### Database Models

**Menu Items:**
```python
class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    image_url = Column(String(200))
    ingredients = Column(Text)  # JSON string
    size_options = Column(Text)  # JSON string
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

**Orders:**
```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(100))  # From token
    agent_id = Column(String(100))  # From OBO token
    customer_info = Column(Text)  # JSON string
    items = Column(Text)  # JSON string
    total_amount = Column(Float)
    status = Column(String(20), default="pending")
    token_type = Column(String(20))  # "user" or "obo"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## 🔍 Pydantic Models & Validation

### Request Models

```python
class CreateOrderRequest(BaseModel):
    """Request model for creating new orders"""
    items: List[OrderItem]
    customer_info: Optional[Dict[str, Any]] = None

class OrderItem(BaseModel):
    """Order item model with validation"""
    menu_item_id: int
    quantity: int = Field(gt=0)  # Must be positive
    size: str = "medium"
    special_instructions: Optional[str] = None
```

### Response Models

```python
class OrderResponse(BaseModel):
    """Response model for order information"""
    id: int
    order_id: str
    user_id: Optional[str]
    agent_id: Optional[str]
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    token_type: str
    created_at: datetime
```

## 🧪 Testing the API

### Using Interactive Documentation

1. Visit http://localhost:8000/docs
2. Click "Authorize" and enter your JWT token
3. Test endpoints interactively with validation

### cURL Examples with Scope Testing

```bash
# Get menu (public endpoint)
curl http://localhost:8000/api/menu

# Get token info (any valid token)
curl -H "Authorization: Bearer your-jwt-token" \
     http://localhost:8000/api/token-info

# Create order (requires order:write scope)
curl -X POST \
     -H "Authorization: Bearer your-write-token" \
     -H "Content-Type: application/json" \
     -d '{"items":[{"menu_item_id":1,"quantity":2,"size":"large"}]}' \
     http://localhost:8000/api/orders

# Get user orders (requires order:read scope)
curl -H "Authorization: Bearer your-read-token" \
     http://localhost:8000/api/orders

# Admin endpoints have been removed - not used by pizza-shack frontend

# Test insufficient permissions (should return 403)
curl -H "Authorization: Bearer token-without-order-scopes" \
     http://localhost:8000/api/orders
```

### Generate Test Tokens

Use the included test script to generate tokens with different scopes:

```bash
python test_scope_validation.py
```

### Example Responses

**Menu Response:**
```json
[
  {
    "id": 1,
    "name": "Margherita Classic",
    "description": "Timeless classic with vibrant San Marzano tomato sauce",
    "price": 12.50,
    "category": "classic",
    "image_url": "/images/margherita_classic.jpeg",
    "ingredients": ["Fresh mozzarella", "San Marzano tomato sauce", "Basil"],
    "size_options": ["Small ($10.50)", "Medium ($12.50)", "Large ($14.50)"],
    "available": true
  }
]
```

**Order Response:**
```json
{
  "id": 1,
  "order_id": "ORD-20241201120000-2",
  "user_id": "user123",
  "agent_id": "pizza-ai-agent",
  "items": [
    {
      "menu_item_id": 1,
      "name": "Margherita Classic",
      "quantity": 2,
      "size": "large",
      "unit_price": 12.50,
      "total_price": 25.00,
      "special_instructions": "Extra cheese"
    }
  ],
  "total_amount": 25.00,
  "status": "confirmed",
  "token_type": "obo",
  "created_at": "2024-12-01T12:00:00Z"
}
```

## 🌐 Deployment

### Local Development

```bash
# Start with auto-reload
uvicorn main:app --reload

# Start with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000
```

### WSO2 Choreo Deployment

1. **Component Configuration (.choreo/component.yaml):**

```yaml
apiVersion: v1alpha1
kind: component
spec:
  name: pizza-api
  type: service
  language: python
  buildSpec:
    context: /pizza-api
    dockerfile: Dockerfile
  endpoints:
  - name: pizza-api
    service:
      basePath: /
      port: 8000
```

2. **Environment Variables:**

```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/pizzashack
CORS_ORIGINS=https://your-frontend.choreoapis.dev
```

## 🔧 Error Handling

### Consistent Error Responses

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            timestamp=datetime.now(timezone.utc).isoformat()
        ).dict()
    )
```

### Standard Error Format

```json
{
  "error": "Menu item 999 not found",
  "status_code": 404,
  "timestamp": "2024-12-01T12:00:00Z"
}
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the right directory
cd pizza-api

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Issues:**
```bash
# Check SQLite permissions
ls -la pizza_shack.db

# Reset database
rm pizza_shack.db
# Restart the server to recreate
```

**Token Issues:**
```bash
# Debug token decoding
curl -H "Authorization: Bearer token" \
     http://localhost:8000/api/token-info

# Validate token format manually
python -c "import jwt; print(jwt.decode('token', options={'verify_signature': False}))"
```

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WSO2 Choreo Documentation](https://wso2.com/choreo/docs/)

## 🔄 Migration from Previous Version

The refactored API maintains **100% backward compatibility** with existing endpoints while providing:

- **Improved Structure**: Modular architecture following FastAPI best practices
- **Better Validation**: Strong typing with Pydantic models
- **Enhanced Error Handling**: Consistent error responses
- **Proper Logging**: Structured logging with request details
- **Extensible Auth**: Scope-based authorization framework

All existing API consumers will continue to work without changes.