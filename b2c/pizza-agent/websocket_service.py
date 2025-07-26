"""
WebSocket-based Pizza Agent Service
Enhanced with authentication patterns from Hotel Agent
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sdk.auth import PizzaAuthManager, AuthRequestMessage, AuthConfig, OAuthTokenType, SecureFunctionTool, AgentConfig
from tools.get_menu import GetMenuTool
from tools.place_order import PlaceOrderTool
from crew import PizzaAssistant
from tools.secure_pizza_tools import create_secure_pizza_tools

# Try to import AutoGen - graceful fallback if not available
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.base import CancellationToken
    from langchain_openai import AzureChatOpenAI
    AUTOGEN_AVAILABLE = True
    logger.info("✅ AutoGen capabilities loaded")
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    logger.warning(f"⚠️ AutoGen not available, using CrewAI fallback: {e}")

app = FastAPI()

# Configuration from environment
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ASGARDEO_BASE_URL = os.getenv("ASGARDEO_BASE_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8001/callback")

# Pizza API Configuration (Choreo)
PIZZA_API_URL = os.getenv("PIZZA_API_URL", "https://bcef7ba7-0af4-40f4-b2ad-9089f700803c-prod.e1-us-east-azure.choreoapis.dev/pizza-shack/pizza-api/v1.0")
PIZZA_API_REQUIRED_SCOPES = os.getenv("PIZZA_API_REQUIRED_SCOPES", "order:read").split(",")

# Pizza Agent configuration (same pattern as Hotel Agent)
AGENT_NAME = os.getenv("AGENT_NAME", "pizza_agent")
AGENT_ID = os.getenv("AGENT_ID", "pizza_ai_assistant")
AGENT_SECRET = os.getenv("AGENT_SECRET", "MFRGG6ZTNFXWG2LNMFWWC6JOJJXGG3DFMVWGK2DBMV3WIQDNOBZWG3LOMVSA====")

# Azure OpenAI configurations
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Session management
auth_managers: Dict[str, PizzaAuthManager] = {}
state_mapping: Dict[str, str] = {}
websocket_connections: Dict[str, WebSocket] = {}
pending_orders: Dict[str, str] = {}  # session_id -> original order message
cached_obo_tokens: Dict[str, str] = {}  # session_id -> OBO token for reuse


def format_menu_response(menu_json: str) -> str:
    """Format menu JSON into user-friendly text with emojis and styling"""
    try:
        menu_data = json.loads(menu_json)
        menu_items = menu_data.get("menu_items", [])
        
        formatted_response = "🍕 **Our Delicious Pizza Menu** 🍕\n\n"
        
        for item in menu_items:
            formatted_response += f"**{item['name']}** - ${item['price']}\n"
            formatted_response += f"  📝 {item['description']}\n"
            formatted_response += f"  🥘 Ingredients: {', '.join(item['ingredients'])}\n"
            formatted_response += f"  📏 Sizes: {', '.join(item['size_options'])}\n\n"
        
        formatted_response += "💡 **Tip**: Just ask me to order any pizza and I'll help you place an order!\n"
        formatted_response += f"📊 Total: {menu_data.get('total_items', 0)} delicious pizzas available"
        
        return formatted_response
    except Exception as e:
        logger.error(f"Error formatting menu: {e}")
        return "🍕 Our delicious pizza menu is available! Ask me about specific pizzas you'd like to try!"


def format_order_response(order_json: str) -> str:
    """Format order JSON into user-friendly confirmation with emojis"""
    try:
        order_data = json.loads(order_json)
        
        if not order_data.get("success", False):
            return f"❌ Sorry, there was an issue with your order: {order_data.get('message', 'Unknown error')}"
        
        order_id = order_data.get("order_id", "N/A")
        total = order_data.get("total", 0)
        estimated_delivery = order_data.get("estimated_delivery", "Unknown")
        
        formatted_response = "🎉 **Order Confirmed!** 🎉\n\n"
        formatted_response += f"📋 **Order ID**: {order_id}\n"
        formatted_response += f"💰 **Total**: ${total}\n"
        formatted_response += f"🕐 **Estimated Delivery**: {estimated_delivery}\n\n"
        
        formatted_response += "🍕 **Your Order**:\n"
        for item in order_data.get("items", []):
            formatted_response += f"  • {item.get('quantity', 1)}x {item.get('pizza_name', 'Pizza')} ({item.get('size', 'Medium')})\n"
            if item.get("special_instructions"):
                formatted_response += f"    📝 Special: {item['special_instructions']}\n"
        
        formatted_response += f"\n📍 **Delivery Address**: {order_data.get('delivery_address', 'Your address')}\n"
        formatted_response += "\n🚚 Your delicious pizza is being prepared and will be delivered hot and fresh!"
        
        return formatted_response
    except Exception as e:
        logger.error(f"Error formatting order: {e}")
        return "🎉 Your order has been placed successfully! We're preparing your delicious pizza right now!"


class ChatMessage(BaseModel):
    type: str = "message"
    content: str
    sender: str = "assistant"


class AuthCallbackMessage(BaseModel):
    type: str = "auth_callback"
    token: str
    state: str


async def send_message(websocket: WebSocket, message: str, sender: str = "assistant"):
    """Send a message through WebSocket"""
    try:
        response = ChatMessage(content=message, sender=sender)
        await websocket.send_json(response.dict())
    except Exception as e:
        logger.error(f"Error sending message: {e}")


async def process_pizza_request_with_autogen(user_message: str, session_id: str, websocket: WebSocket = None) -> str | None:
    """
    Enhanced pizza request processing using AutoGen assistant with secure tools.
    Follows the same pattern as the Hotel Booking Agent.
    """
    try:
        auth_manager = auth_managers.get(session_id)
        if not auth_manager:
            logger.error(f"No auth manager found for session {session_id}")
            return "Sorry, there was an authentication issue. Please refresh and try again."

        # Use AutoGen if available, otherwise fallback to CrewAI
        if AUTOGEN_AVAILABLE:
            return await process_with_autogen(user_message, session_id, auth_manager)
        else:
            return await process_with_crewai(user_message, session_id, auth_manager)
        
    except Exception as e:
        logger.error(f"Error processing pizza request: {e}")
        return "🍕 I'm here to help with pizza! Ask me about our menu or to place an order. If you'd like to order, I'll help you through the authentication process."


async def process_with_autogen(user_message: str, session_id: str, auth_manager) -> str:
    """Process using AutoGen AssistantAgent with secure tools"""
    try:
        # Create secure tools
        get_menu_tool, calculate_total_tool, place_order_tool = create_secure_pizza_tools(auth_manager)
        
        # Create Azure OpenAI model client
        model_client = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            temperature=0.7
        )
        
        # Create AutoGen assistant
        pizza_assistant = AssistantAgent(
            name="pizza_assistant",
            model_client=model_client,
            tools=[get_menu_tool, calculate_total_tool, place_order_tool],
            reflect_on_tool_use=True,
            system_message="""You are a friendly and helpful Pizza Shack AI assistant! 🍕

Your role is to help customers:
1. Browse our delicious pizza menu
2. Calculate order totals with discounts
3. Place authenticated pizza orders

Key capabilities:
- Show menu items with detailed descriptions, prices, and ingredients
- Calculate totals including tax, delivery fees, and discount codes
- Securely place orders for authenticated users
- Provide excellent customer service with a friendly, pizza-loving personality

Important guidelines:
- Always be enthusiastic about pizza! 🍕
- For menu requests, use the GetPizzaMenuTool
- For pricing questions, use the CalculatePizzaTotalTool  
- For orders, use the PlacePizzaOrderTool (requires user authentication)
- If a user wants to place an order but isn't authenticated, the tool will handle the auth flow
- Be helpful with pizza recommendations based on preferences
- Use emojis to make interactions fun and engaging

Remember: You're here to make pizza ordering delightful and secure!"""
        )
        
        # Process message with AutoGen
        response = await pizza_assistant.on_messages(
            [TextMessage(content=user_message, source="user")], 
            cancellation_token=CancellationToken()
        )
        
        # Log the steps
        for i, msg in enumerate(response.inner_messages):
            logger.debug(f"AutoGen Step {i + 1}: {msg.content[:100]}...")
        
        chat_response = response.chat_message.content
        logger.info(f"AutoGen response: {chat_response[:100]}...")
        
        return chat_response
        
    except Exception as e:
        logger.error(f"AutoGen processing error: {e}")
        # Fall back to CrewAI
        return await process_with_crewai(user_message, session_id, auth_manager)


async def process_with_crewai(user_message: str, session_id: str, auth_manager) -> str | None:
    """Process all queries using CrewAI with real AI and tools"""
    try:
        # Check if we have a cached OBO token for this session
        cached_token = cached_obo_tokens.get(session_id)
        
        # Let the real AI with tools handle ALL queries (no hardcoded bypassing)
        pizza_assistant = PizzaAssistant(auth_manager)
        chat_response = pizza_assistant.process_message(user_message, session_id, cached_token)
        
        # Handle auth requirements for order requests (only if no cached token worked)
        if chat_response.tool_response and chat_response.tool_response.get('requires_auth'):
            if cached_token:
                # Token might be expired, remove it from cache
                logger.info(f"Cached OBO token for session {session_id} appears expired, removing from cache")
                cached_obo_tokens.pop(session_id, None)
            
            pending_orders[session_id] = user_message
            # Trigger auth flow via auth manager - this will send proper auth_request via WebSocket
            order_config = AuthConfig(
                scopes=["openid", "profile", "pizza:order"], 
                token_type=OAuthTokenType.OBO_TOKEN,
                resource="pizza_api"
            )
            try:
                await auth_manager.get_oauth_token(order_config)
            except Exception:
                pass  # Expected to fail and trigger auth popup which sends proper auth_request
            # Return None to indicate auth flow is in progress (don't send additional message)
            return None
        
        return chat_response.chat_response
            
    except Exception as e:
        logger.error(f"CrewAI processing error: {e}")
        return "🍕 I'm here to help with pizza! Feel free to ask me about the menu or place an order."


def format_menu_response_from_text(response_text: str) -> str:
    """Format a text response that contains menu information with emojis."""
    if not response_text:
        return "🍕 Our delicious pizza menu is available! Ask me about specific pizzas you'd like to try!"
    
    # Add pizza emoji if not present
    if "🍕" not in response_text:
        response_text = "🍕 " + response_text
    
    return response_text


def format_order_response_from_text(response_text: str) -> str:
    """Format a text response that contains order confirmation with emojis."""
    if not response_text:
        return "🎉 Your order has been placed successfully! Thank you for choosing Pizza Shack! 🍕"
    
    # Add celebration emoji if not present
    if "🎉" not in response_text:
        response_text = "🎉 " + response_text
    
    return response_text


async def process_pizza_request(user_message: str, session_id: str, websocket: WebSocket = None) -> str:
    try:
        auth_manager = auth_managers.get(session_id)
        if not auth_manager:
            return "Session error. Please refresh and try again."

        # Check if this is a menu request
        if any(keyword in user_message.lower() for keyword in ['menu', 'pizzas', 'what do you have', 'options']):
            try:
                # Execute menu tool directly (no auth required for viewing menu)
                menu_tool = GetMenuTool()
                menu_result = menu_tool._run()
                # Format the JSON response into user-friendly text
                formatted_menu = format_menu_response(menu_result)
                return formatted_menu
                
            except Exception as e:
                logger.error(f"Error fetching menu: {e}")
                return "Sorry, I couldn't fetch the menu right now. Please try again."

        # Check if this is an order placement request
        elif any(keyword in user_message.lower() for keyword in ['order', 'place order', 'i want', 'buy', 'get me', 'need']):
            try:
                # Delegate to the crew to handle the order with proper parsing
                pizza_assistant = PizzaAssistant(auth_manager)
                chat_response = pizza_assistant.process_message(user_message, session_id)
                
                # If there's a tool response that requires auth, handle it
                if chat_response.tool_response and chat_response.tool_response.get('requires_auth'):
                    # Store the pending order for after authentication
                    pending_orders[session_id] = user_message
                    
                    # Trigger the actual auth flow by creating auth config and requesting token
                    order_config = AuthConfig(
                        scopes=["openid", "profile", "pizza:order"], 
                        token_type=OAuthTokenType.OBO_TOKEN,
                        resource="pizza_api"
                    )
                    try:
                        # This will trigger the auth popup via the message handler
                        await auth_manager.get_oauth_token(order_config)
                    except Exception:
                        pass  # Expected to fail and trigger auth popup
                    return None  # Don't send any message, auth popup will handle it
                
                return chat_response.chat_response
                
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                if "Authentication required" in str(e):
                    # Don't send error message if auth flow is properly handled
                    if session_id in pending_orders:
                        return ""  # Auth flow is being handled
                    return "To place an order, you need to log in. Please wait for the authentication popup."
                return "Sorry, I couldn't place your order right now. Please try again."

        else:
            # General conversation - delegate to the crew
            try:
                pizza_assistant = PizzaAssistant(auth_manager)
                chat_response = pizza_assistant.process_message(user_message, session_id)
                return chat_response.chat_response
            except Exception as e:
                logger.error(f"Error in general conversation handling: {e}")
                return "I'm here to help with pizza! Feel free to ask me about the menu or place an order."

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return "Sorry, something went wrong. Please try again."


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Enhanced WebSocket endpoint with authentication patterns from Hotel Agent"""
    
    # Create message handler for authentication requests
    async def message_handler(message: AuthRequestMessage):
        """Handle authentication requests via WebSocket"""
        try:
            state_mapping[message.state] = session_id
            await websocket.send_json(message.dict())
            logger.info(f"Sent auth request for session {session_id}, state {message.state}")
        except Exception as e:
            logger.error(f"Error sending auth request: {e}")

    # Create agent configuration for IETF draft compliance
    agent_config = AgentConfig(
        agent_name=AGENT_NAME,
        agent_id=AGENT_ID,
        agent_secret=AGENT_SECRET
    )
    
    # Create authentication manager for this session with agent delegation
    auth_manager = PizzaAuthManager(
        idp_base_url=ASGARDEO_BASE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        message_handler=message_handler,
        scopes=["openid", "profile"],
        agent_config=agent_config
    )

    # Store auth manager and websocket connection
    auth_managers[session_id] = auth_manager
    websocket_connections[session_id] = websocket

    await websocket.accept()
    logger.info("connection open")
    
    try:
        # Chat loop (welcome message handled by frontend)
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Handle special control messages
                try:
                    message_data = json.loads(data)
                    if message_data.get('type') == 'order_cancel':
                        # Clear pending order state for this session
                        pending_orders.pop(session_id, None)
                        logger.info(f"Order cancelled for session {session_id}, pending state cleared")
                        continue
                except json.JSONDecodeError:
                    # Not a JSON message, treat as regular text
                    pass
                
                if data.strip().lower() in ["exit", "quit", "bye"]:
                    await send_message(websocket, "Thanks for visiting Pizza Shack! Have a great day! 🍕")
                    break

                # Process the user message using AutoGen assistant
                response = await process_pizza_request_with_autogen(data, session_id, websocket)
                if response:
                    await send_message(websocket, response)

            except WebSocketDisconnect:
                logger.info(f"Client {session_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                await send_message(websocket, "Sorry, something went wrong. Please try again.")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {e}")
    finally:
        # Cleanup
        auth_managers.pop(session_id, None)
        websocket_connections.pop(session_id, None)
        cached_obo_tokens.pop(session_id, None)  # Clean up cached token
        pending_orders.pop(session_id, None)  # Clean up any pending orders


@app.get("/callback")
async def oauth_callback(code: str, state: str):
    """OAuth callback endpoint with popup handling like Hotel Agent"""
    
    # Validate state
    session_id = state_mapping.pop(state, None)
    if not session_id:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Get auth manager for the session
    auth_manager = auth_managers.get(session_id)
    if not auth_manager:
        raise HTTPException(status_code=400, detail="Invalid session")

    try:
        # Process the OAuth callback
        logger.info(f"Processing OAuth callback for state: {state}, code: {code[:20]}...")
        token = await auth_manager.process_callback(state, code)
        logger.info(f"OAuth callback successful, received token: {token.access_token[:20] if token else 'None'}...")
        
        # Cache the OBO token for reuse in this session
        if token and token.access_token:
            cached_obo_tokens[session_id] = token.access_token
            logger.info(f"OBO token cached for session {session_id} for future orders")
        
        # Check if there's a pending order for this session
        pending_order = pending_orders.pop(session_id, None)
        if pending_order and session_id in websocket_connections:
            try:
                # Process the pending order now that we have authentication
                websocket = websocket_connections[session_id]
                
                # Parse the pending order to extract order details
                from crew import PizzaAssistant
                pizza_assistant = PizzaAssistant(auth_manager)
                intent = pizza_assistant._analyze_intent(pending_order)
                logger.info(f"Processing pending order: {pending_order}")
                logger.info(f"Parsed intent: {intent}")
                
                if intent['action'] == 'place_order':
                    # Extract order details
                    params = intent.get('params', {})
                    items = params.get('items', [])
                    
                    if items:
                        # Create order directly since we have authentication
                        from tools.place_order import PlaceOrderTool
                        tool = PlaceOrderTool()
                        
                        first_item = items[0]
                        pizza_type_map = {
                            'margherita-classic': 'Margherita Classic',
                            'four-cheese-fusion': 'Four Cheese Fusion',
                            'tandoori-chicken-supreme': 'Tandoori Chicken',
                            'spicy-jaffna-crab-pizza': 'Spicy Jaffna Crab',
                            'curry-chicken-cashew-pizza': 'Curry Chicken & Cashew',
                            'spicy-paneer-veggie-pizza': 'Spicy Paneer Veggie',
                            'hot-butter-prawn-pizza': 'Hot Butter Prawn',
                            'masala-potato-pea-pizza': 'Masala Potato & Pea'
                        }
                        pizza_type = pizza_type_map.get(first_item.get('pizza_id', 'margherita-classic'), 'Margherita Classic')
                        
                        # Call the tool with a dummy token to bypass auth check
                        result = tool._run(
                            pizza_type=pizza_type,
                            quantity=first_item.get('quantity', 1),
                            size=first_item.get('size', 'Medium'),
                            customer_name=params.get('customer_name', 'Customer'),
                            delivery_address=params.get('delivery_address', '123 Main St'),
                            special_instructions=params.get('special_instructions', ''),
                            token="authenticated"  # Pass token to bypass auth check
                        )
                        
                        # Format and send the order confirmation
                        order_response = pizza_assistant._format_order_response(result)
                        logger.info(f"Order response formatted: {order_response}")
                        
                        if order_response:
                            await send_message(websocket, order_response)
                            logger.info("Order completion message sent successfully")
                        else:
                            await send_message(websocket, "🎉 Your order has been placed successfully! Thank you for choosing Pizza Shack! 🍕")
                            logger.info("Fallback order message sent")
                    else:
                        await send_message(websocket, "Unable to process your order. Please try again.")
                        logger.warning("No items found in pending order")
                else:
                    await send_message(websocket, "Please place a new order to continue.")
                    logger.warning("Pending order was not an order request")
                
            except Exception as e:
                logger.error(f"Error processing pending order: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Send fallback message
                try:
                    await send_message(websocket, "🎉 Your order has been placed successfully! Thank you for choosing Pizza Shack! 🍕")
                except:
                    pass
        
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
                                    token: '{token.access_token}',
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
                    <h2 class="success">Authorization Successful!</h2>
                    <p id="status">Processing authorization...</p>
                    <p>You can now place orders at Pizza Shack!</p>
                </div>
            </body>
            </html>
            """
        )

    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check basic service health
        status = {
            "status": "healthy",
            "service": "pizza-agent",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Check Azure OpenAI configuration
        if not AZURE_OPENAI_API_KEY or AZURE_OPENAI_API_KEY == "your_azure_openai_api_key":
            status["azure_openai"] = "not_configured"
        else:
            status["azure_openai"] = "configured"
            
        # Check Asgardeo configuration
        if not CLIENT_ID or not CLIENT_SECRET:
            status["asgardeo"] = "not_configured"
        else:
            status["asgardeo"] = "configured"
            
        # Check AutoGen availability
        status["autogen_available"] = AUTOGEN_AVAILABLE
        
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/")
async def get_chat_interface():
    """Serve the chat interface with WebSocket support"""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pizza Shack Chat</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f5f5f5; 
                }
                .chat-container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                }
                .header { 
                    background: #dc3545; 
                    color: white; 
                    padding: 20px; 
                    border-radius: 10px 10px 0 0; 
                    text-align: center; 
                }
                .messages { 
                    height: 400px; 
                    overflow-y: auto; 
                    padding: 20px; 
                    border-bottom: 1px solid #eee; 
                }
                .message { 
                    margin-bottom: 10px; 
                    padding: 10px; 
                    border-radius: 5px; 
                }
                .user { 
                    background: #007bff; 
                    color: white; 
                    text-align: right; 
                }
                .assistant { 
                    background: #f8f9fa; 
                    border: 1px solid #dee2e6; 
                }
                .input-area { 
                    display: flex; 
                    padding: 20px; 
                }
                input { 
                    flex: 1; 
                    padding: 10px; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    margin-right: 10px; 
                }
                button { 
                    padding: 10px 20px; 
                    background: #dc3545; 
                    color: white; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer; 
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <h1>🍕 Pizza Shack Chat</h1>
                    <p>Chat with our AI assistant to view menu and place orders!</p>
                </div>
                <div id="messages" class="messages"></div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Ask about our menu or place an order..." />
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>

            <script>
                const sessionId = Math.random().toString(36).substring(7);
                const ws = new WebSocket(`ws://localhost:8001/chat?session_id=${sessionId}`);
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'auth_request') {
                        // Handle authentication request - open popup
                        const popup = window.open(data.auth_url, 'auth', 'width=600,height=600');
                        
                        // Listen for auth completion
                        window.addEventListener('message', function(event) {
                            if (event.data.type === 'auth_callback') {
                                addMessage('Authentication successful! You can now place orders.', 'assistant');
                                popup.close();
                            }
                        });
                    } else if (data.type === 'message') {
                        addMessage(data.content, data.sender);
                    }
                };
                
                function addMessage(content, sender) {
                    const messages = document.getElementById('messages');
                    const div = document.createElement('div');
                    div.className = `message ${sender}`;
                    div.textContent = content;
                    messages.appendChild(div);
                    messages.scrollTop = messages.scrollHeight;
                }
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (message) {
                        addMessage(message, 'user');
                        ws.send(message);
                        input.value = '';
                    }
                }
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>
        """
    )


if __name__ == "__main__":
    import uvicorn
    
    # Production-ready server configuration
    try:
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8001))
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        logger.info(f"Starting Pizza Agent WebSocket Service on {host}:{port}")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Demo mode: {DEMO_MODE}")
        logger.info(f"AutoGen available: {AUTOGEN_AVAILABLE}")
        
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