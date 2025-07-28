"""
 Copyright (c) 2025, WSO2 LLC. (http://www.wso2.com). All Rights Reserved.

  This software is the property of WSO2 LLC. and its suppliers, if any.
  Dissemination of any information or reproduction of any material contained
  herein is strictly forbidden, unless permitted by WSO2 in accordance with
  the WSO2 Commercial License available at http://wso2.com/licenses.
  For specific language governing the permissions and limitations under
  this license, please see the license as well as any agreement you’ve
  entered into with WSO2 governing the purchase of this software and any
"""

import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv

from sdk.auth import OAuthToken

load_dotenv()

pizza_api_base_url = os.environ.get('PIZZA_API_BASE_URL', 'http://localhost:8000')


def _format_menu_display(menu_data: dict) -> str:
    """Helper function to format menu data for display"""
    formatted_menu = "🍕 **PIZZA SHACK MENU** 🍕\n\n"
    
    # Group by category
    categories = {"classic": "🏆 CLASSIC", "premium": "⭐ PREMIUM", "specialty": "🌶️ SPECIALTY", "vegetarian": "🥬 VEGETARIAN"}
    
    for category, emoji_title in categories.items():
        category_pizzas = [p for p in menu_data.get("pizzas", []) if p.get("category") == category]
        if category_pizzas:
            formatted_menu += f"**{emoji_title}**\n"
            for pizza in category_pizzas:
                formatted_menu += f"• **{pizza['name']}** - ${pizza['price']:.2f}\n"
                formatted_menu += f"  _{pizza['description']}_\n"
                if pizza.get('ingredients'):
                    ingredients_display = ', '.join(pizza['ingredients'][:3])
                    if len(pizza['ingredients']) > 3:
                        ingredients_display += "..."
                    formatted_menu += f"  🥘 {ingredients_display}\n\n"
                else:
                    formatted_menu += "\n"
    
    formatted_menu += "All pizzas come in Medium size and include free delivery! 🚚\n"
    formatted_menu += "Simply say 'Order [Pizza Name]' to place your order! 😊"
    
    return formatted_menu


async def _get(base_url: str, path: str, bearer_token: str, params: dict = None) -> dict:
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "X-JWT-Assertion": bearer_token,  # Add JWT assertion header for Pizza API
        "Accept": "application/json"
    }

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_menu(token: Optional[OAuthToken] = None) -> dict:
    """Fetch pizza menu - hybrid approach: try API first, fallback to hardcoded menu"""
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("📋 FETCHING MENU (Hybrid Approach)")
    
    # Try to fetch from Pizza API first
    try:
        logger.info("🌐 Attempting to fetch menu from Pizza API...")
        
        async with httpx.AsyncClient() as client:
            # No authentication required for menu endpoint, but add Choreo API key if available
            headers = {"Accept": "application/json"}
            
            # Add Choreo API key header if configured
            choreo_api_key = os.environ.get('CHOREO_API_KEY')
            if choreo_api_key:
                headers["apikey"] = choreo_api_key
            
            url = f"{pizza_api_base_url}/api/menu"
            
            logger.info(f"📤 GET {url}")
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            api_menu_response = response.json()
            
            # The API returns an array of pizzas, so we need to wrap it
            if isinstance(api_menu_response, list):
                api_menu_data = {"pizzas": api_menu_response}
            else:
                api_menu_data = api_menu_response
                
            logger.info(f"✅ MENU FETCHED FROM API - {len(api_menu_data.get('pizzas', []))} pizzas available")
            
            # Format the API response for display
            formatted_menu = _format_menu_display(api_menu_data)
            api_menu_data["formatted_display"] = formatted_menu
            api_menu_data["source"] = "api"
            
            return api_menu_data
            
    except Exception as e:
        logger.warning(f"⚠️ API menu fetch failed: {str(e)}")
        logger.info("🔄 Falling back to hardcoded menu...")
    
    # Fallback to hardcoded menu data
    try:
        logger.info("📋 Using hardcoded fallback menu...")
        
        # Menu data (aligned with existing pizza-agent prices)
        menu_data = {
            "pizzas": [
                
                {
                    "id": 1,
                    "name": "Tandoori Chicken",
                    "description": "Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce",
                    "price": 14.99,
                    "category": "specialty",
                    "ingredients": ["Tandoori chicken", "Bell peppers", "Red onions", "Mozzarella cheese", "Spiced tomato sauce", "Indian herbs"]
                },
                {
                    "id": 2,
                    "name": "Spicy Jaffna Crab",
                    "description": "Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!",
                    "price": 16.50,
                    "category": "specialty",
                    "ingredients": ["Jaffna crab curry", "Mozzarella cheese", "Red onions", "Chili flakes", "Curry leaves", "Coconut milk base"]
                },
                {
                    "id": 3,
                    "name": "Curry Chicken & Cashew",
                    "description": "Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!",
                    "price": 13.99,
                    "category": "specialty",
                    "ingredients": ["Sri Lankan chicken curry", "Roasted cashews", "Mozzarella cheese", "Curry sauce", "Fresh coriander"]
                },
                {
                    "id": 4,
                    "name": "Spicy Paneer Veggie",
                    "description": "Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella",
                    "price": 13.50,
                    "category": "vegetarian",
                    "ingredients": ["Marinated paneer", "Bell peppers", "Red onions", "Tomatoes", "Mozzarella cheese", "Spiced tomato base"]
                },
                {
                    "id": 5,
                    "name": "Margherita Classic",
                    "description": "Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves",
                    "price": 12.50,
                    "category": "classic",
                    "ingredients": ["Fresh mozzarella", "San Marzano tomato sauce", "Whole basil leaves", "Extra virgin olive oil", "Sea salt"]
                },
                {
                    "id": 6,
                    "name": "Four Cheese Fusion", 
                    "description": "A cheese lover's dream with mozzarella, sharp cheddar, Parmesan, and creamy ricotta",
                    "price": 13.25,
                    "category": "premium",
                    "ingredients": ["Mozzarella", "Sharp cheddar", "Parmesan", "Creamy ricotta", "Artisan crust", "Olive oil"]
                },
                {
                    "id": 7,
                    "name": "Hot Butter Prawn",
                    "description": "Juicy prawns in signature hot butter sauce with mozzarella and spring onions",
                    "price": 15.50,
                    "category": "specialty",
                    "ingredients": ["Juicy prawns", "Hot butter sauce", "Mozzarella cheese", "Spring onions", "Garlic", "Chili flakes"]
                },
                {
                    "id": 8,
                    "name": "Masala Potato & Pea",
                    "description": "Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella",
                    "price": 12.99,
                    "category": "vegetarian",
                    "ingredients": ["Spiced potatoes", "Green peas", "Mozzarella cheese", "Masala spices", "Fresh coriander", "Cumin"]
                }
            ]
        }
        
        # Format the fallback menu display
        formatted_menu = _format_menu_display(menu_data)
        menu_data["formatted_display"] = formatted_menu
        menu_data["source"] = "fallback"
        
        logger.info(f"✅ FALLBACK MENU LOADED - {len(menu_data['pizzas'])} pizzas available")
        return menu_data
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Both API and fallback menu failed - {str(e)}")
        return {"error": f"Failed to fetch menu: {str(e)}"}


async def place_pizza_order(pizza_name: str, quantity: int = 1, 
                           customer_name: str = "Demo Customer", 
                           delivery_address: str = "123 Pizza Street, Demo City",
                           special_instructions: Optional[str] = None,
                           token: Optional[OAuthToken] = None) -> dict:
    """Place a pizza order using authenticated user token - simplified ordering"""
    
    import logging
    import time
    import uuid
    from datetime import datetime, timedelta
    
    logger = logging.getLogger(__name__)
    
    # Log token info if environment variable is set
    if os.environ.get('ENABLE_TOKEN_LOGGING', 'false').lower() == 'true' and token:
        logger.info("🔐" * 10 + " TOKEN LOGGING ENABLED " + "🔐" * 10)
        logger.info(f"📝 ACCESS TOKEN (PREVIEW): {token.access_token[:30]}...{token.access_token[-10:] if len(token.access_token) > 40 else token.access_token}")
        
        # Try to decode token for debugging
        try:
            import jwt
            payload = jwt.decode(token.access_token, options={"verify_signature": False})
            logger.info(f"📋 TOKEN PAYLOAD:")
            logger.info(f"   ├─ Subject (User): {payload.get('sub')}")
            logger.info(f"   ├─ Scopes: {payload.get('scope')}")
            logger.info(f"   ├─ Audience: {payload.get('aud')}")
            logger.info(f"   ├─ Issuer: {payload.get('iss')}")
            if 'act' in payload:
                agent_info = payload.get('act', {})
                if isinstance(agent_info, dict):
                    logger.info(f"   ├─ Acting Agent ID: {agent_info.get('sub')}")
                else:
                    logger.info(f"   ├─ Acting Agent: {agent_info}")
            logger.info(f"   └─ Expires At: {datetime.fromtimestamp(payload.get('exp', 0)).isoformat() if payload.get('exp') else 'Unknown'}")
        except Exception as e:
            logger.info(f"⚠️ Could not decode token: {e}")
        logger.info("🔐" * 50)
    
    if not token:
        return {"error": "Authentication required to place orders", "requires_auth": True}
    
    # Get menu to fetch pizza details for better ordering
    menu = await fetch_menu()
    
    # Pizza name to menu item ID mapping
    pizza_mapping = {
        "Tandoori Chicken": 1,
        "tandoori": 1,
        "tandoori chicken": 1,
        "Spicy Jaffna Crab": 2,
        "spicy jaffna crab": 2,
        "jaffna crab": 2,
        "crab": 2,
        "Curry Chicken & Cashew": 3,
        "curry chicken": 3,
        "curry chicken & cashew": 3,
        "curry chicken and cashew": 3,
        "Spicy Paneer Veggie": 4,
        "spicy paneer": 4,
        "spicy paneer veggie": 4,
        "paneer": 4,
        "Margherita Classic": 5,
        "margherita": 5,
        "margherita classic": 5,
        "Four Cheese Fusion": 6,
        "four cheese": 6,
        "four cheese fusion": 6,
        "cheese": 6,
        "Hot Butter Prawn": 7,
        "hot butter prawn": 7,
        "butter prawn": 7,
        "prawn": 7,
        "Masala Potato & Pea": 8,
        "masala potato": 8,
        "masala potato & pea": 8,
        "masala potato and pea": 8,
        "potato": 8
    }
    
    # Find the menu item ID for the pizza
    pizza_name_lower = pizza_name.lower().strip()
    menu_item_id = pizza_mapping.get(pizza_name_lower)
    
    # Find pizza details from menu
    pizza_details = None
    if "pizzas" in menu:
        for pizza in menu["pizzas"]:
            if pizza["id"] == menu_item_id:
                pizza_details = pizza
                break
    
    if not menu_item_id:
        # Try partial matching
        for pizza_key, item_id in pizza_mapping.items():
            if pizza_key.lower() in pizza_name_lower or pizza_name_lower in pizza_key.lower():
                menu_item_id = item_id
                # Update pizza details
                if "pizzas" in menu:
                    for pizza in menu["pizzas"]:
                        if pizza["id"] == item_id:
                            pizza_details = pizza
                            break
                break
    
    if not menu_item_id:
        return {"error": f"Pizza '{pizza_name}' not found in our menu. Please check the menu and try again."}
    
    # Extract user info from token if available
    from datetime import datetime
    user_id = "demo_user"
    agent_id = "e88695cf-4d55-4b38-9840-011f1d31028f"  # Default agent ID
    
    # Try to extract user and agent info from token
    if token:
        try:
            # Use base64 and json for JWT decoding without signature verification
            import base64
            import json
            
            # Split JWT token into parts
            token_parts = token.access_token.split('.')
            if len(token_parts) >= 2:
                # Decode the payload (second part)
                payload_b64 = token_parts[1]
                # Add padding if needed
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += '=' * padding
                
                payload_json = base64.urlsafe_b64decode(payload_b64)
                payload = json.loads(payload_json)
                
                logger.info(f"🔍 Decoded JWT payload: {payload}")
                
                # Extract user ID from token
                extracted_user_id = payload.get('sub')
                if extracted_user_id:
                    user_id = extracted_user_id
                    logger.info(f"✅ Extracted user ID from OBO token: {user_id}")
                else:
                    logger.warning(f"⚠️ No 'sub' found in token payload, using default: {user_id}")
                
                # Extract agent ID from act claim  
                if 'act' in payload:
                    agent_info = payload.get('act', {})
                    if isinstance(agent_info, dict):
                        extracted_agent_id = agent_info.get('sub')
                        if extracted_agent_id:
                            agent_id = extracted_agent_id
                            logger.info(f"✅ Extracted agent ID from OBO token: {agent_id}")
                            
            else:
                logger.error(f"❌ Invalid JWT token format - expected 3 parts, got {len(token_parts)}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to decode OBO token: {e}")
            logger.warning(f"⚠️ Using default user_id: {user_id}, agent_id: {agent_id}")
    
    correlation_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    logger.info(f"🍕 ORDER REQUEST - {correlation_id}")
    logger.info(f"   ├─ Pizza: {pizza_name} (ID: {menu_item_id})")
    logger.info(f"   ├─ Quantity: {quantity}")
    logger.info(f"   ├─ Customer: {customer_name}")
    logger.info(f"   ├─ Address: {delivery_address}")
    logger.info(f"   ├─ User ID: {user_id}")
    logger.info(f"   └─ Agent ID: {agent_id}")
    
    async with httpx.AsyncClient() as client:
        # Set the authorization headers with the access token (OBO token)
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "X-JWT-Assertion": token.access_token,  # Add JWT assertion header for Pizza API
            "Content-Type": "application/json"
        }
        
        # Calculate total amount (simplified - using pizza price)
        total_amount = pizza_details['price'] * quantity if pizza_details else 15.00 * quantity
        
        order_data = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "id": 0,  # Will be assigned by server
            "items": [{
                "menu_item_id": menu_item_id,
                "quantity": quantity,
                "size": "medium",  # lowercase as per API spec
                "special_instructions": special_instructions or ""
            }],
            "order_id": str(uuid.uuid4()),  # Generate unique order ID
            "status": "pending",
            "token_type": "Bearer",
            "total_amount": total_amount,
            "user_id": user_id
        }

        try:
            # Debug: Log the request body
            logger.info(f"📤 ORDER PAYLOAD - {correlation_id}")
            logger.info(f"   ├─ URL: {pizza_api_base_url}/api/orders")
            logger.info(f"   ├─ Request Body: {order_data}")
            logger.info(f"   └─ Headers: {headers}")
            
            # Make the POST request to the pizza orders endpoint
            response = await client.post(
                f"{pizza_api_base_url}/api/orders",
                json=order_data,
                headers=headers,
                timeout=15
            )

            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Return the JSON response
            order_result = response.json()
            duration = (time.time() - start_time) * 1000
            
            logger.info(f"✅ ORDER SUCCESS - {correlation_id} ({duration:.0f}ms)")
            logger.info(f"   ├─ Order ID: {order_result.get('order_id')}")
            logger.info(f"   ├─ Status: {order_result.get('status')}")
            logger.info(f"   └─ Total: ${order_result.get('total_amount')}")
            
            # Create comprehensive order summary
            if "order_id" in order_result:
                # Calculate estimated delivery time
                delivery_time = datetime.now() + timedelta(minutes=35)
                estimated_delivery = delivery_time.strftime("%I:%M %p")
                
                # Build detailed order summary
                order_summary = f"""🎉 **ORDER CONFIRMED!** 🎉

📋 **Order Details:**
   • Order ID: #{order_result.get('order_id')}
   • Pizza: {pizza_details['name'] if pizza_details else pizza_name} (Medium)
   • Quantity: {quantity}
   • Delivery Address: {delivery_address}"""
                
                if special_instructions:
                    order_summary += f"\n   • Special Instructions: {special_instructions}"
                
                order_summary += f"""

💰 **Total Amount: ${order_result.get('total_amount')}**

🚚 **Delivery Info:**
   • Status: {order_result.get('status', 'Confirmed').title()}
   • Estimated Delivery: {estimated_delivery}
   • Order Time: {datetime.now().strftime('%I:%M %p')}

Thank you for choosing Pizza Shack! Your delicious {pizza_details['name'] if pizza_details else pizza_name} will be prepared fresh and delivered hot! 🍕✨"""
                
                order_result["order_summary"] = order_summary
                order_result["success_message"] = order_summary
            
            return order_result
            
        except httpx.HTTPStatusError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ ORDER FAILED - {correlation_id} ({duration:.0f}ms)")
            logger.error(f"   ├─ Status Code: {e.response.status_code}")
            logger.error(f"   └─ Response: {e.response.text}")
            
            if e.response.status_code == 401:
                return {"error": "Authentication failed", "requires_auth": True}
            elif e.response.status_code == 403:
                return {"error": "Insufficient permissions", "requires_auth": True}
            else:
                return {"error": f"Order failed: {e.response.text}"}
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ ORDER ERROR - {correlation_id} ({duration:.0f}ms)")
            logger.error(f"   └─ Error: {str(e)}")
            return {"error": f"Failed to place order: {str(e)}"}
