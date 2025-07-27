"""
WebSocket-only Pizza Agent Service
Simplified version focused on WebSocket communication only
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Literal, Dict, Optional

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect

from app.prompt import agent_system_prompt
from app.tools import fetch_menu, place_pizza_order
from autogen.tool import SecureFunctionTool
from sdk.auth import AuthRequestMessage, AuthManager, AuthSchema, AuthConfig, AgentConfig, OAuthTokenType
from fastapi.responses import FileResponse

# Configure logging with better formatting
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

load_dotenv()

# Demo mode configuration
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

templates = Jinja2Templates(directory="static")

# Asgardeo related configurations
client_id = os.environ.get('ASGARDEO_CLIENT_ID')
client_secret = os.environ.get('ASGARDEO_CLIENT_SECRET')
idp_base_url = os.environ.get('ASGARDEO_TENANT_DOMAIN')
redirect_url = os.environ.get('ASGARDEO_REDIRECT_URI', 'http://localhost:8001/callback')

# Azure OpenAI configs
azure_openai_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
azure_openai_api_version = os.environ.get('AZURE_OPENAI_API_VERSION')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextResponse(BaseModel):
    type: Literal["message"] = "message"
    content: str

# Initialize model client only if not in demo mode
model_client = None
if not DEMO_MODE:
    try:
        model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=deployment_name,
            api_version=azure_openai_api_version,
            azure_endpoint=azure_openai_endpoint,
            model="gpt-4o"
        )
        logger.info("Azure OpenAI model client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Azure OpenAI client: {e}, falling back to demo mode")
        DEMO_MODE = True
else:
    logger.info("Running in demo mode with rule-based responses")

auth_managers: Dict[str, AuthManager] = {}
pizza_assistants: Dict[str, AssistantAgent] = {}
state_mapping: Dict[str, str] = {}

async def run_agent(assistant: Optional[AssistantAgent], websocket: WebSocket, session_id: str):
    # Start the chat loop
    while True:
        user_input = await websocket.receive_text()
        request_start_time = datetime.now()
        
        logger.info(f"📝 Received message from {session_id}: {user_input[:100]}...")

        if user_input.strip().lower() == "exit":
            await websocket.close()
            break

        # Handle AI mode
        if assistant is not None:
            try:
                # Send the user message to the AI agent
                response = await assistant.on_messages(
                    [TextMessage(content=user_input, source="user")], 
                    cancellation_token=CancellationToken()
                )

                response_content = response.chat_message.content
                
                # Check if any tool response contains authentication requirements
                auth_required = False
                for msg in response.inner_messages:
                    if hasattr(msg, 'content') and isinstance(msg.content, str):
                        try:
                            if "requires_auth" in msg.content and "true" in msg.content.lower():
                                auth_required = True
                                break
                        except Exception:
                            pass
                
                # If authentication is required, the AuthManager should handle it
                if auth_required:
                    logger.info(f"Authentication required for session {session_id}")
                    response_content = "🔐 Authentication required to place your order. Please check for the authorization popup."
            
            except Exception as e:
                logger.error(f"Error in agent processing for session {session_id}: {str(e)}", exc_info=True)
                response_content = "Sorry, I encountered an error processing your request. Please try again."
        else:
            # Fallback response when no assistant is available
            response_content = "I'm here to help with pizza orders! You can ask me to 'show the menu' or 'order a pizza'."

        # Log outgoing response
        duration_ms = (datetime.now() - request_start_time).total_seconds() * 1000
        logger.info(f"📤 Response to {session_id} ({duration_ms:.0f}ms): {response_content[:100]}...")
        
        # Send the response back to the client
        await websocket.send_json(TextResponse(content=response_content).model_dump())

@app.get('/')
async def index(request: Request):
    WS_BASE_URL = os.getenv("WS_BASE_URL", "ws://localhost:8001")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ws_base_url": WS_BASE_URL
    })

@app.get('/health')
async def health():
    return {
        "status": "healthy", 
        "service": "pizza-agent-websocket-only",
        "demo_mode": DEMO_MODE,
        "model_client_available": model_client is not None,
        "agent_config": {
            "agent_id": os.environ.get('AGENT_ID'),
            "agent_name": os.environ.get('AGENT_NAME'),
            "has_agent_secret": bool(os.environ.get('AGENT_SECRET'))
        }
    }

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat functionality"""

    # Check if session already exists
    if session_id in auth_managers:
        logger.info(f"🔄 Reusing existing session {session_id}")
        # Close the existing WebSocket if there's a new connection
        # This handles React StrictMode and other cases where multiple connections are attempted
        existing_auth_manager = auth_managers[session_id]
    else:
        logger.info(f"🆕 Creating new session {session_id}")

    # Create callback function to handle auth request redirects
    async def message_handler(message: AuthRequestMessage):
        state_mapping[message.state] = session_id
        logger.info(f"WebSocket: Sending auth request for session {session_id}, state {message.state}")
        await websocket.send_json(message.model_dump())

    # Create a auth manager instance for the chat session (only if not exists)
    auth_manager = auth_managers.get(session_id)
    if not auth_manager and not DEMO_MODE:
        try:
            auth_manager = AuthManager(
                idp_base_url,
                client_id,
                client_secret,
                redirect_url,
                message_handler,
                agent_config=AgentConfig(
                    agent_id=os.environ.get('AGENT_ID'),
                    agent_secret=os.environ.get('AGENT_SECRET'),
                ))
            
            logger.info(f"✅ AuthManager created successfully for session {session_id}")
            
        except Exception as auth_init_error:
            logger.error(f"❌ Failed to create AuthManager for session {session_id}: {str(auth_init_error)}")
            auth_manager = None

        # Store the auth manager by session_id
        if auth_manager:
            auth_managers[session_id] = auth_manager

        # Create the set of tools required for pizza ordering
        fetch_menu_tool = None
        place_order_tool = None
        
        if auth_manager:
            fetch_menu_tool = SecureFunctionTool(
                fetch_menu,
                description="Fetches the pizza menu with all available pizzas, prices, and descriptions",
                name="FetchMenuTool",
                auth=None,  # No authentication required for viewing menu
                strict=False
            )

            place_order_tool = SecureFunctionTool(
                place_pizza_order,
                description="Places a pizza order for the authenticated user",
                name="PlacePizzaOrderTool",
                auth=AuthSchema(auth_manager, AuthConfig(
                    scopes=["order:write", "openid", "profile"],
                    token_type=OAuthTokenType.OBO_TOKEN,
                    resource="pizza_api"
                )),
                strict=False
            )

    # Create agent instance for the chat session (only if not in demo mode and not cached)
    pizza_assistant = pizza_assistants.get(session_id)
    if not pizza_assistant and not DEMO_MODE and model_client is not None and auth_manager and fetch_menu_tool and place_order_tool:
        pizza_assistant = AssistantAgent(
            "pizza_ordering_assistant",
            model_client=model_client,
            tools=[fetch_menu_tool, place_order_tool],
            reflect_on_tool_use=True,
            system_message=agent_system_prompt)
        pizza_assistants[session_id] = pizza_assistant
        logger.info(f"✅ Pizza Assistant created successfully for session {session_id}")
    elif pizza_assistant:
        logger.info(f"🔄 Reusing existing Pizza Assistant for session {session_id}")
    else:
        logger.warning(f"⚠️ Pizza Assistant not created - Demo: {DEMO_MODE}, Model: {model_client is not None}, Auth: {auth_manager is not None}")

    # Initiate WebSocket connection
    await websocket.accept()

    try:
        # Send a single welcome message
        welcome_msg = "Welcome to Pizza Shack! 🍕 I'm here to help you browse our menu and place delicious pizza orders. What can I do for you today?"
        await websocket.send_json(TextResponse(content=welcome_msg).model_dump())

        # Continue to run the agent
        await run_agent(pizza_assistant, websocket, session_id)
    except WebSocketDisconnect:
        logger.info(f"Client with session_id {session_id} disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
    finally:
        # Don't immediately remove sessions to handle React StrictMode and reconnections
        # Sessions will be cleaned up after a timeout or on server restart
        logger.info(f"WebSocket connection closed for session {session_id}, keeping session data for potential reconnection")

@app.get("/callback")
async def callback(code: str, state: str):
    """OAuth callback endpoint"""
    
    # Debug: Log the callback request
    logger.info(f"🔵 Callback received: state={state}, code={code[:20]}...")
    
    # Check if the state is valid
    session_id = state_mapping.pop(state, None)
    if not session_id:
        logger.error(f"🔴 Invalid state '{state}' - not found in state mapping")
        raise HTTPException(status_code=400, detail="Invalid state.")

    logger.info(f"🔵 Found session_id {session_id} for state {state}")

    # Get the auth manager for the session
    auth_manager = auth_managers.get(session_id)
    if not auth_manager:
        logger.error(f"🔴 No auth manager found for session {session_id}")
        raise HTTPException(status_code=400, detail="Invalid session.")

    try:
        token = await auth_manager.process_callback(state, code)
        logger.info(f"✅ Callback processed successfully for state {state}")

        # Return success page
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pizza Shack - Authorization Successful</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 50px;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        max-width: 500px;
                        margin: 0 auto;
                        padding: 20px;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .success {{
                        color: #28a745;
                        margin-bottom: 20px;
                    }}
                    .pizza-emoji {{
                        font-size: 3em;
                        margin-bottom: 10px;
                    }}
                </style>
                <script>
                    function communicateAndClose() {{
                        if (window.opener) {{
                            try {{
                                const message = {{
                                    type: 'auth_callback',
                                    token: '{getattr(token, "access_token", "success")}',
                                    state: '{state}',
                                    success: true
                                }};

                                // Notify parent window
                                window.opener.postMessage(message, "*");

                                // Update status
                                document.getElementById('status').textContent = 
                                    'Authorization successful! You can now place orders. Closing window...';

                                // Close window after delay
                                setTimeout(function() {{
                                    window.close();
                                }}, 2000);
                            }} catch (err) {{
                                console.error('Error communicating with parent window:', err);
                                document.getElementById('status').textContent = 'Error: ' + err.message;
                            }}
                        }} else {{
                            document.getElementById('status').textContent = 
                                'Please return to the Pizza Shack chat to continue.';
                        }}
                    }}

                    window.onload = communicateAndClose;
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="pizza-emoji">🍕</div>
                    <h1 class="success">Authorization Successful!</h1>
                    <p id="status">You can now place your pizza order!</p>
                    <p><small>This window will close automatically...</small></p>
                </div>
            </body>
            </html>
            """
        )

    except Exception as e:
        logger.error(f"❌ Error processing OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    try:
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8001))
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        logger.info(f"Starting Pizza Agent WebSocket-Only Service on {host}:{port}")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Demo mode: {DEMO_MODE}")
        
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level=log_level,
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise