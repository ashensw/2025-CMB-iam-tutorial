# Pizza Shack Application Architecture Guide

## Table of Contents
1. [Overall Architecture](#overall-architecture)
2. [Frontend Analysis](#frontend-analysis)
3. [Backend Analysis](#backend-analysis)
4. [Integration Patterns](#integration-patterns)
5. [Code Quality Assessment](#code-quality-assessment)
6. [Development Workflow](#development-workflow)
7. [Improvement Recommendations](#improvement-recommendations)

## Overall Architecture

### High-Level System Design
The Pizza Shack application follows a modern client-server architecture with clear separation of concerns:

```
┌─────────────────┐    WebSocket        ┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   React SPA     │◄───────────────────►│  Pizza Agent    │◄─────────────────│   Pizza API     │
│   (Frontend)    │                     │  AutoGen        │                  │  (Business)     │
│   Port: 5173    │    HTTP/REST        │   Port: 8001    │                  │   Port: 8000    │
│                 │◄───────────────────►│                 │                  │                 │
└─────────────────┘                     └─────────────────┘                  └─────────────────┘
         │                                       │                                       │
         │                                       │                                       │
         ▼                                       ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐                     ┌─────────────────┐
│   Asgardeo      │                     │   AutoGen       │                     │   Database      │
│   (Auth)        │                     │   + Azure       │                     │   (Menu/Orders) │
└─────────────────┘                     │   OpenAI        │                     │                 │
                                        └─────────────────┘                     └─────────────────┘

┌─────────────────┐
│ Pizza Riders    │    (Separate App for Delivery Staff Registration)
│   React SPA     │
│   Port: 5174    │
│                 │
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│   Asgardeo      │
│   (Auth +       │
│   Identity      │
│   Verification) │
└─────────────────┘
```

### Technology Stack

**Frontend (pizza-shack/)**
- **Framework**: React 19 with Vite
- **Authentication**: @asgardeo/auth-react
- **Language**: JavaScript (ESM)
- **Styling**: CSS + Inline Styles
- **Build Tool**: Vite

**Pizza Riders App (pizza-shack-riders/)**
- **Framework**: React 19 with Vite + TypeScript
- **Authentication**: @asgardeo/auth-react
- **Identity Verification**: Onfido SDK integration
- **UI Library**: Material-UI + Oxygen UI
- **Language**: TypeScript
- **Build Tool**: Vite

**Pizza Agent (pizza-agent-autogen/)**
- **Framework**: FastAPI with WebSocket support
- **AI/ML**: Microsoft AutoGen + Azure OpenAI (GPT-4)
- **Authentication**: JWT with PyJWT + OAuth callback handling
- **Server**: Uvicorn with WebSocket support
- **Language**: Python 3.11+

**Pizza API (pizza-api/)**
- **Framework**: FastAPI
- **Database**: JSON-based data storage
- **Authentication**: JWT token validation with scopes
- **Server**: Uvicorn
- **Language**: Python 3.11+

## Frontend Analysis

### Project Structure
```
pizza-shack/
├── src/
│   ├── App.jsx                 # Main application component
│   ├── App.css                 # Global styles
│   ├── main.jsx               # Entry point
│   ├── components/
│   │   └── ChatBot.jsx        # Chat interface component
│   └── assets/
├── public/
│   └── images/                # Static assets
├── package.json
├── vite.config.js
└── index.html
```

### Component Architecture

**App.jsx** - Root Component
- Handles authentication state with `useAuthContext`
- Implements conditional rendering (Login vs Main App)
- Two-panel layout: Menu (left) + Chat (right)
- Manages local UI state with `useState`

**Key Patterns:**
```javascript
// Authentication Integration
const { state } = useAuthContext();

// Conditional Rendering
{state.isAuthenticated ? (
  <div className="app-container">
    {/* Main App UI */}
  </div>
) : (
  <div className="login-container">
    {/* Login UI */}
  </div>
)}
```

### State Management Strategy
- **Global Auth State**: Asgardeo AuthContext
- **Local UI State**: React useState hooks
- **No complex state management**: Redux/Zustand not needed for current scope

### Styling Approach
- **Global CSS**: App.css for base styles
- **Inline Styles**: Extensive use for dynamic styling
- **Visual Design**: Modern UI with gradients, shadows, rounded corners

## Backend Analysis

### Project Structure
```
pizza-agent-autogen/
├── app/
│   ├── service.py             # FastAPI application entry
│   ├── prompt.py              # AI agent prompt configuration
│   ├── tools.py               # AutoGen agent tools
│   └── __init__.py
├── autogen/
│   └── tool.py                # AutoGen tool wrapper
├── sdk/
│   └── auth.py                # Authentication handling
├── static/
│   └── index.html             # Agent frontend interface
├── requirements.txt
├── .env.example
├── openapi.yaml               # API specification
└── Dockerfile
```

### API Endpoints

| Endpoint | Method | Protected | Purpose |
|----------|--------|-----------|---------|
| `/` | GET | No | Welcome message |
| `/health` | GET | No | Health check |
| `/menu` | GET | No | Fetch pizza menu |

### AI Integration Architecture

**AutoGen Pattern:**
```python
# Assistant Agent Configuration
assistant = AssistantAgent(
    name="pizza_assistant",
    system_message=PIZZA_ASSISTANT_PROMPT,
    llm_config={
        "model": "gpt-4o",
        "api_key": AZURE_OPENAI_API_KEY,
        "base_url": AZURE_OPENAI_ENDPOINT,
        "api_type": "azure",
        "api_version": AZURE_OPENAI_API_VERSION
    }
)

# User Proxy for Tool Execution
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False
)

# Chat Execution
chat_result = user_proxy.initiate_chat(
    assistant,
    message=user_message,
    max_turns=3
)
```

### WebSocket Implementation

**Real-time Chat Service (`app/service.py`):**
```python
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    auth_manager = PizzaAuthManager(session_id)
    
    async for message in websocket.iter_text():
        data = json.loads(message)
        response = await process_chat_message(data, auth_manager)
        await websocket.send_text(json.dumps(response))
```

**Authentication Flow Management:**
```python
class PizzaAuthManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pending_actions = {}
    
    def initiate_auth_flow(self, action_data):
        # Generate unique auth URL for popup authentication
        auth_url = f"{AUTH_BASE_URL}/authorize?..."
        return {"type": "auth_request", "auth_url": auth_url}
```

### AutoGen Integration Architecture

**Agent Configuration:**
```python
# System prompt for pizza assistant behavior
PIZZA_ASSISTANT_PROMPT = """
You are a friendly and helpful Pizza Shack assistant. Your role is to:
- Help customers browse our delicious pizza menu
- Assist with pizza recommendations based on preferences
- Guide customers through the ordering process
- Provide accurate information about pricing and ingredients
- Maintain a warm, welcoming tone throughout the conversation
"""

# Assistant with tool registration
assistant = AssistantAgent(
    name="pizza_assistant",
    system_message=PIZZA_ASSISTANT_PROMPT,
    llm_config=llm_config
)

# Register tools for function calling
register_function(
    get_menu_tool,
    caller=assistant,
    executor=user_proxy,
    description="Get the current pizza menu with categories and pricing"
)
```

**Tool Execution Pattern:**
```python
# AutoGen tool wrapper
def get_menu_tool() -> str:
    """Retrieve the current pizza menu from the API."""
    try:
        response = requests.get(f"{PIZZA_API_BASE_URL}/api/menu")
        if response.status_code == 200:
            menu_data = response.json()
            return format_menu_response(menu_data)
        return "Unable to fetch menu at this time"
    except Exception as e:
        return f"Error retrieving menu: {str(e)}"
```

**Available AutoGen Tools:**
- **get_menu_tool**: Fetches menu from Pizza API with category filtering
- **place_order_tool**: Places authenticated orders via Pizza API
- **calculate_total_tool**: Computes order totals with tax and discounts

## Integration Patterns & Data Flow

### Complete AI-Powered Ordering Flow

**Example: User Orders a Pizza via AI**

1. **User Input**: "I want to order a large Tandoori Chicken pizza"
2. **WebSocket Transmission**: Frontend sends message to Pizza Agent via WebSocket
3. **AutoGen Processing**: 
   - LLM analyzes intent (order placement)
   - Extracts entities (pizza type, size)
   - Calls `place_order_tool` function
4. **Authentication Check**: Tool verifies user has valid access token
5. **Auth Flow (if needed)**:
   - Agent sends `auth_request` via WebSocket
   - Frontend opens Asgardeo popup
   - User authenticates, callback processed
   - Order proceeds with valid tokens
6. **API Call**: Tool makes authenticated POST to Pizza API `/orders`
7. **Database Update**: Pizza API stores order in database
8. **Confirmation**: Success flows back through the chain
9. **AI Response**: LLM formats confirmation for user
10. **WebSocket Response**: "Great! Your large Tandoori Chicken pizza is on its way. Order ID: 12345 🎉"

### Authentication Patterns

**Standard Frontend Auth:**
```javascript
// Asgardeo OAuth 2.0 integration
const { state, signIn, getAccessToken } = useAuthContext();

// Direct API calls with Bearer token
const response = await fetch('http://localhost:8001/api/orders', {
  headers: { 'Authorization': `Bearer ${await getAccessToken()}` }
});
```

**AI-Triggered Authentication:**
```javascript
// WebSocket message handling for auth requests
if (message.type === 'auth_request') {
  const popup = window.open(message.auth_url, 'auth', 'width=500,height=600');
  // Handle popup completion and resume AI flow
}
```

### Communication Patterns

**WebSocket for Real-time Chat:**
```javascript
const ws = new WebSocket(`ws://localhost:8001/chat?session_id=${sessionId}`);
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.type === 'chat_response') {
    displayMessage(response.content);
  } else if (response.type === 'auth_request') {
    handleAuthRequest(response);
  }
};
```

**REST API for Business Operations:**
```python
# Pizza API endpoints
@app.get("/menu")  # Public menu access
@app.post("/orders", dependencies=[Depends(verify_jwt)])  # Protected ordering
@app.get("/orders/{user_id}", dependencies=[Depends(verify_jwt)])  # User orders
```

### Error Handling Strategy
- Backend: HTTP status codes + JSON error responses
- Frontend: Try-catch blocks with user-friendly messages
- Graceful degradation for AI service unavailability

## Code Quality Assessment

### Strengths
✅ **Clear Separation of Concerns**: Frontend/backend boundaries well-defined
✅ **Modular AI Architecture**: AutoGen tool-based agent system extensible
✅ **Environment Configuration**: Proper .env usage for secrets
✅ **Demo Mode Support**: Fallback for development without external services
✅ **Modern Frameworks**: React 19 + FastAPI + AutoGen cutting-edge stack

## Development Workflow

### Quick Start
```bash
# Start all services with one command
cd b2c
./start_pizza_shack.sh

# Check service status
./start_pizza_shack.sh --status

# Stop all services
./stop_pizza_shack.sh
```

### Manual Setup Process
```bash
# Backend setup
cd pizza-agent-autogen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.service:app --host 0.0.0.0 --port 8001 --reload

# Frontend setup
cd pizza-shack
npm install
npm run dev

# Riders app setup
cd pizza-shack-riders
npm install
npm run dev
```

### Development Servers
- **Frontend**: `http://localhost:5173` (Vite dev server)
- **Riders App**: `http://localhost:5174` (Vite dev server)
- **Pizza Agent**: `http://localhost:8001` (Uvicorn with auto-reload)
- **Pizza API**: `http://localhost:8000` (Uvicorn with auto-reload)
- **API Docs**: `http://localhost:8001/docs` (FastAPI auto-generated)

### Environment Management
- **Development**: `.env` files for configuration
- **Demo Mode**: `DEMO_MODE=true` for offline development
- **Production**: Environment-specific variable injection
