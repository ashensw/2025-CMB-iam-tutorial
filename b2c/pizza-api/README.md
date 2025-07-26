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

## � Authorization Configuration

The Pizza API supports **flexible authorization handling** that can adapt to different deployment environments:

### 🔄 Two Authorization Modes

#### 1. Backend Validation Mode (Default)
The API validates JWT tokens directly and enforces scope-based authorization:

```bash
# .env configuration
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=true
```

**Behavior:**
- ✅ Validates JWT token signature and claims
- ✅ Enforces scope-based authorization per endpoint
- ✅ Detailed logging of token analysis
- ✅ Supports multiple token types (user, agent, OBO)

#### 2. Gateway Authorization Mode (Choreo/API Gateway)
When deployed with gateway-level OAuth2 enforcement, the backend skips validation:

```bash
# .env configuration for Choreo deployment
ENABLE_BACKEND_TOKEN_VALIDATION=false
AUTH_HEADER_NAME=X-Access-Token
ENABLE_TOKEN_LOGGING=true
```

**Behavior:**
- 🚫 Backend skips JWT validation (gateway handles it)
- ✅ Creates placeholder token data for business logic
- ✅ Maintains API compatibility
- ✅ Logs incoming headers for debugging

### 🎛️ Configuration Options

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `ENABLE_BACKEND_TOKEN_VALIDATION` | boolean | `true` | Toggle JWT validation in backend |
| `AUTH_HEADER_NAME` | string | `Authorization` | Header name for JWT token extraction |
| `ENABLE_TOKEN_LOGGING` | boolean | `true` | Enable detailed token logging |

### 📄 OpenAPI Integration

The API automatically validates scopes based on the OpenAPI specification:

```yaml
# Example from openapi.yaml
/api/orders:
  post:
    security:
      - BearerAuth: ['order:write']
  get:
    security:
      - BearerAuth: ['order:read']
```

**Scope Mapping:**
- `POST /api/orders` → `order:write`
- `GET /api/orders` → `order:read`
- `GET /api/orders/{id}` → `order:read`
- `GET /api/system/status` → *no scopes required*

### 🔐 JWT Validation Methods

The API supports two JWT validation approaches:

#### 1. JWKS Validation (Recommended for Production)
```bash
# .env configuration
ENABLE_BACKEND_TOKEN_VALIDATION=true
JWKS_URL=https://api.asgardeo.io/t/your-org/oauth2/jwks
JWT_ALGORITHM=RS256
JWT_ISSUER=https://api.asgardeo.io/t/your-org/oauth2/token
JWT_AUDIENCE=pizza-app
```

**Benefits:**
- ✅ Automatic key rotation support
- ✅ Full signature verification
- ✅ Industry standard approach
- ✅ Enhanced security

#### 2. Static Secret Key (Development/Testing)
```bash
# .env configuration
ENABLE_BACKEND_TOKEN_VALIDATION=true
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
```

**Note:** JWKS takes precedence if both `JWKS_URL` and `JWT_SECRET_KEY` are provided.

### 🪵 Enhanced Token Logging

When `ENABLE_TOKEN_LOGGING=true`, the API provides comprehensive logging:

**Backend Validation Mode:**
```log
🔑 [AUTH DEBUG] Validating JWT token with JWKS: eyJ0eXAiOiJKV1Qi...
✅ [AUTH DEBUG] Retrieved signing key from JWKS
✅ [AUTH DEBUG] JWT signature validation successful
📋 [AUTH DEBUG] JWT payload: {"sub": "user123", "scope": "order:read order:write", ...}
📊 [AUTH DEBUG] JWT Claims Analysis:
  ├─ sub (Subject): user123
  ├─ aud (Audience): pizza-app
  ├─ iss (Issuer): https://api.asgardeo.io/t/org/oauth2/token
  ├─ exp (Expires): 1640995200
  ├─ scope: order:read order:write
  └─ act (Actor): N/A
👤 [AUTH DEBUG] Detected User token - User: user123
✅ [AUTH DEBUG] Token validation successful - all required scopes present
```

**Gateway Mode:**
```log
🔑 [AUTH DEBUG] Decoding JWT token (no validation): eyJ0eXAiOiJKV1Qi...
✅ [AUTH DEBUG] JWT decoded successfully (no validation)
🚫 [AUTH DEBUG] Backend validation disabled - using JWT for business context only
```

### 🚀 Usage Examples

#### Backend Validation Mode (.env)
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=true
```

**Request:**
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." \
     -X POST http://localhost:8000/api/orders \
     -d '{"items": [{"menu_item_id": 1, "quantity": 2}]}'
```

#### Gateway Mode (.env)
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=false
AUTH_HEADER_NAME=X-Access-Token
ENABLE_TOKEN_LOGGING=true
```

**Expected Behavior:**
- Gateway validates JWT and forwards request
- Backend receives request (potentially without Authorization header)
- Backend creates placeholder token data and processes business logic
- All endpoints remain functional

### 🌐 Header Support

The API supports extracting tokens from multiple header formats:

| Header Format | Example | Use Case |
|--------------|---------|----------|
| `Authorization: Bearer <token>` | Standard OAuth2 | Direct API access |
| `X-Access-Token: <token>` | Custom header | API Gateway forwarding |
| `X-JWT-Assertion: <token>` | Choreo format | WSO2 Choreo deployment |

## �🛠️ Local Development Setup

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

### Environment Configuration

Create a `.env` file with the following configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/pizzashack
# For local development: DATABASE_URL=sqlite:///./pizza_shack.db

# Server Configuration
PORT=8000
HOST=0.0.0.0

# JWT/OAuth2 Configuration
JWKS_URL=https://api.asgardeo.io/t/your-org/oauth2/jwks
# Alternative: JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=RS256
JWT_ISSUER=https://api.asgardeo.io/t/your-org/oauth2/token
JWT_AUDIENCE=pizza-app

# Authorization Configuration (NEW)
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=true

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CORS_METHODS=*
CORS_HEADERS=*
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO

# WSO2 Choreo Configuration (for deployment)
CHOREO_PROJECT_ID=your-project-id
CHOREO_ENVIRONMENT=development
```

#### Authorization Configuration Options

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENABLE_BACKEND_TOKEN_VALIDATION` | Enable/disable backend JWT validation | `true` | `false` (for Choreo) |
| `AUTH_HEADER_NAME` | Header name for JWT extraction | `Authorization` | `X-Access-Token` |
| `ENABLE_TOKEN_LOGGING` | Enable detailed token logging | `true` | `false` (production) |

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

**Backend Validation Mode:**
```bash
# Standard Authorization header
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." \
     -X POST http://localhost:8000/api/orders \
     -H "Content-Type: application/json" \
     -d '{"items":[{"menu_item_id":1,"quantity":2}]}'
```

**Custom Header Mode:**
```bash
# Set AUTH_HEADER_NAME=X-Access-Token
curl -H "X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." \
     -X POST http://localhost:8000/api/orders \
     -H "Content-Type: application/json" \
     -d '{"items":[{"menu_item_id":1,"quantity":2}]}'
```

**Gateway Mode (ENABLE_BACKEND_TOKEN_VALIDATION=false):**
```bash
# No token validation - gateway handles it
curl -X POST http://localhost:8000/api/orders \
     -H "Content-Type: application/json" \
     -d '{"items":[{"menu_item_id":1,"quantity":2}]}'
```

**Test Authorization Logging:**
```bash
# Enable detailed logging: ENABLE_TOKEN_LOGGING=true
curl -H "Authorization: Bearer your-jwt-token" \
     http://localhost:8000/api/token-info

# Check logs for detailed JWT analysis
```

### Testing Different Authorization Scenarios

**Scenario 1: Backend Validation (Local Development)**
```bash
# .env configuration
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=true

# Expected: Full JWT validation and scope checking
```

**Scenario 2: Gateway Mode (Choreo Deployment)**
```bash
# .env configuration  
ENABLE_BACKEND_TOKEN_VALIDATION=false
AUTH_HEADER_NAME=X-Access-Token
ENABLE_TOKEN_LOGGING=true

# Expected: No backend validation, placeholder token data
```

**Scenario 3: Custom Header**
```bash
# .env configuration
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=X-Custom-Token
ENABLE_TOKEN_LOGGING=true

# Expected: JWT extracted from X-Custom-Token header
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

2. **Environment Variables for Different Deployments:**

**Local Development (.env):**
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=true
DATABASE_URL=sqlite:///./pizza_shack.db
```

**Choreo with JWT Forwarding (Hybrid Mode):**
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=false
AUTH_HEADER_NAME=X-JWT-Assertion
ENABLE_TOKEN_LOGGING=true
DATABASE_URL=postgresql://prod-url
```

**Choreo without JWT (Pure Gateway Mode):**
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=false
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=false
DATABASE_URL=postgresql://prod-url
```

**Standalone Production (.env):**
```bash
ENABLE_BACKEND_TOKEN_VALIDATION=true
AUTH_HEADER_NAME=Authorization
ENABLE_TOKEN_LOGGING=false
DATABASE_URL=postgresql://prod-url
```

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

## � Troubleshooting Authorization

### Common Issues

**1. 401 Unauthorized in Gateway Mode**
```bash
# Problem: Backend validation enabled but no token provided
# Solution: Disable backend validation for gateway deployment
ENABLE_BACKEND_TOKEN_VALIDATION=false
```

**2. Token Not Found in Custom Header**
```bash
# Problem: Token sent in wrong header
# Solution: Check AUTH_HEADER_NAME configuration
AUTH_HEADER_NAME=X-Access-Token  # Match your gateway configuration
```

**3. No Token Logging**
```bash
# Problem: Not seeing detailed token analysis in logs
# Solution: Enable token logging
ENABLE_TOKEN_LOGGING=true
```

**4. Scope Validation Fails**
```bash
# Problem: 403 Forbidden even with valid token
# Solution: Check if token contains required scopes
# Required scopes: order:read, order:write
```

### Debug Commands

```bash
# Test different authorization modes
python test_flexible_auth.py

# Check server logs for token analysis
tail -f logs/api.log | grep "AUTH DEBUG"

# Test with different headers
curl -H "Authorization: Bearer token" http://localhost:8000/api/token-info
curl -H "X-Access-Token: token" http://localhost:8000/api/token-info
```

## �📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WSO2 Choreo Documentation](https://wso2.com/choreo/docs/)


All existing API consumers will continue to work without changes.