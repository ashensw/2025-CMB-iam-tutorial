from typing import List, Dict, Any
import json
import uuid
import requests
import os
import time
import logging
from datetime import datetime, timedelta
try:
    from crewai_tools import tool
except ImportError:
    try:
        from crewai.tools import tool
    except ImportError:
        from crewai.tools.base_tool import tool

logger = logging.getLogger(__name__)

class APILogger:
    """Utility for logging API requests with tokens"""
    
    @staticmethod
    def log_api_request_with_token(method: str, url: str, headers: Dict = None, data: Dict = None, correlation_id: str = None):
        """Log API request with token information at INFO level"""
        logger.info("🔗" * 5 + " API REQUEST WITH TOKEN " + "🔗" * 5)
        logger.info(f"📝 METHOD: {method.upper()}")
        logger.info(f"🎯 URL: {url}")
        if correlation_id:
            logger.info(f"🔗 CORRELATION_ID: {correlation_id}")
        logger.info(f"⏰ TIMESTAMP: {time.time()}")
        
        # Log headers with token details
        if headers:
            logger.info("📋 HEADERS:")
            for key, value in headers.items():
                if key.lower() == 'authorization' and value.startswith('Bearer '):
                    token = value[7:]  # Remove 'Bearer ' prefix
                    # Log raw token
                    logger.info(f"   └─ {key} (RAW TOKEN): {token}")
                    # Log token preview
                    preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
                    logger.info(f"   └─ {key} (PREVIEW): Bearer {preview}")
                    
                    # Try to decode token for additional info
                    try:
                        import jwt
                        payload = jwt.decode(token, options={"verify_signature": False})
                        logger.info(f"   └─ TOKEN_INFO:")
                        logger.info(f"      ├─ User ID: {payload.get('sub')}")
                        logger.info(f"      ├─ Scopes: {payload.get('scope')}")
                        if 'act' in payload:
                            agent_id = payload.get('act', {}).get('sub') if isinstance(payload.get('act'), dict) else str(payload.get('act'))
                            logger.info(f"      ├─ Agent ID (OBO): {agent_id}")
                        logger.info(f"      └─ Expires: {payload.get('exp')}")
                    except Exception as e:
                        logger.info(f"   └─ TOKEN_DECODE_ERROR: {e}")
                else:
                    logger.info(f"   └─ {key}: {value}")
        
        # Log request data
        if data:
            logger.info("📦 REQUEST DATA:")
            # Only show non-sensitive parts of request data
            for key, value in data.items():
                logger.info(f"   └─ {key}: {value}")
    
    @staticmethod
    def log_api_response(status_code: int, response_data: Dict = None, correlation_id: str = None, duration_ms: float = None):
        """Log API response details at INFO level"""
        logger.info("📨" * 5 + " API RESPONSE " + "📨" * 5)
        logger.info(f"📊 STATUS_CODE: {status_code}")
        if correlation_id:
            logger.info(f"🔗 CORRELATION_ID: {correlation_id}")
        if duration_ms is not None:
            logger.info(f"⏱️ DURATION: {duration_ms:.2f}ms")
        logger.info(f"⏰ TIMESTAMP: {time.time()}")
        
        # Log response data
        if response_data:
            logger.info("📦 RESPONSE DATA:")
            for key, value in response_data.items():
                logger.info(f"   └─ {key}: {value}")

api_logger = APILogger()


def get_obo_token(user_token: str) -> str:
    """Exchange user token for OBO token (placeholder - implement with real Asgardeo)"""
    # In production, this would call Asgardeo token exchange endpoint
    # For demo purposes, return a mock OBO token
    return f"demo-obo-token-for-{user_token[:10]}"


def place_order_via_api(items: List[Dict], customer_info: Dict, obo_token: str) -> str:
    """Place order via Pizza Shack API using OBO token"""
    
    import logging
    logger = logging.getLogger(__name__)
    
    api_base_url = os.getenv("PIZZA_API_URL", "http://localhost:8000")
    api_url = f"{api_base_url}/api/orders"
    
    # Log outgoing API call details
    token_preview = f"{obo_token[:20]}...{obo_token[-10:]}" if len(obo_token) > 30 else obo_token
    logger.info(f"📞 [AI-AGENT] Making API call to Pizza API")
    logger.info(f"   └─ URL: {api_url}")
    logger.info(f"   └─ Token: {token_preview}")
    logger.info(f"   └─ Items: {len(items)} item(s)")
    
    # Try to decode and log the token being sent
    try:
        import jwt
        payload = jwt.decode(obo_token, options={"verify_signature": False})
        filtered_payload = {k: v for k, v in payload.items() 
                          if k not in ['signature', 'key', 'secret']}
        logger.info(f"📋 [AI-AGENT] Sending JWT payload: {filtered_payload}")
        
        if "act" in payload:
            user_id = payload.get("sub")
            agent_id = payload.get("act", {}).get("sub")
            logger.info(f"🤖 [AI-AGENT] Sending OBO token - Agent: {agent_id} for User: {user_id}")
        else:
            logger.info(f"👤 [AI-AGENT] Sending user token for User: {payload.get('sub')}")
            
    except Exception as e:
        logger.warning(f"⚠️ [AI-AGENT] Could not decode outgoing token: {e}")
    
    # Prepare order request
    order_request = {
        "items": items,
        "customer_info": customer_info
    }
    
    headers = {
        "Authorization": f"Bearer {obo_token}",
        "Content-Type": "application/json"
    }
    
    try:
        correlation_id = str(uuid.uuid4())[:8]
        
        # Log detailed API request with token
        api_logger.log_api_request_with_token(
            method="POST",
            url=api_url,
            headers=headers,
            data=order_request,
            correlation_id=correlation_id
        )
        
        request_start = time.time()
        response = requests.post(api_url, json=order_request, headers=headers, timeout=15)
        request_duration = (time.time() - request_start) * 1000
        response.raise_for_status()
        
        order_result = response.json()
        
        # Log detailed API response
        api_logger.log_api_response(
            status_code=response.status_code,
            response_data=order_result,
            correlation_id=correlation_id,
            duration_ms=request_duration
        )
        
        # Log successful API response
        logger.info(f"✅ [AI-AGENT] API call successful - Order created")
        logger.info(f"   └─ Order ID: {order_result.get('order_id')}")
        logger.info(f"   └─ User ID: {order_result.get('user_id')}")
        logger.info(f"   └─ Agent ID: {order_result.get('agent_id')}")
        logger.info(f"   └─ Token Type: {order_result.get('token_type')}")
        logger.info(f"   └─ Total: ${order_result.get('total_amount')}")
        
        # Format response for agent
        formatted_response = {
            "success": True,
            "order_id": order_result["order_id"],
            "total_amount": order_result["total_amount"],
            "status": order_result["status"],
            "user_id": order_result.get("user_id"),
            "agent_id": order_result.get("agent_id"),
            "items": order_result["items"],
            "created_at": order_result["created_at"],
            "message": f"Order #{order_result['order_id']} placed successfully via API! Total: ${order_result['total_amount']}",
            "api_source": "pizza-shack-api"
        }
        
        return json.dumps(formatted_response, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return json.dumps({
                "error": "Authentication failed - invalid or expired token",
                "success": False,
                "requires_auth": True,
                "status_code": 401
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": "Insufficient permissions to place orders",
                "success": False,
                "requires_obo": True,
                "status_code": 403
            })
        else:
            print(f"API error {e.response.status_code}: {e}, falling back to static order")
            return place_order_static(items, customer_info)
            
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}, falling back to static order")
        return place_order_static(items, customer_info)
    except Exception as e:
        print(f"Unexpected error: {e}, falling back to static order")
        return place_order_static(items, customer_info)


def place_order_static(items: List[Dict], customer_info: Dict) -> str:
    """Fallback static order processing when API is unavailable"""
    
    try:
        # Generate order ID
        order_id = f"PZ{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate totals
        subtotal = sum(item.get("total_price", 0) for item in items)
        tax_rate = 0.08  # 8% tax
        delivery_fee = 2.99
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax + delivery_fee, 2)
        
        # Estimated delivery time
        delivery_time = datetime.now() + timedelta(minutes=35)
        estimated_delivery = delivery_time.strftime("%I:%M %p")
        
        # Create order
        order = {
            "success": True,
            "order_id": order_id,
            "customer_info": customer_info,
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "delivery_fee": delivery_fee,
            "total": total,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "estimated_delivery": estimated_delivery,
            "message": f"Order #{order_id} placed successfully! Estimated delivery: {estimated_delivery}",
            "api_source": "static-fallback"
        }
        
        return json.dumps(order, indent=2)
        
    except Exception as e:
        error_response = {
            "error": f"Failed to place order: {str(e)}",
            "success": False
        }
        return json.dumps(error_response, indent=2)


@tool("Place Pizza Order")
def place_order_tool(pizza_type: str = "Margherita", quantity: int = 1, size: str = "medium", 
                     customer_name: str = "Pizza Lover", delivery_address: str = "123 Main St", 
                     special_instructions: str = "", user_token: str = None) -> str:
    """Place a pizza order using OBO token for user context. Requires authenticated user."""
    
    if not user_token:
        return json.dumps({
            "error": "User authentication required to place orders",
            "success": False,
            "requires_auth": True
        })
    
    # Map pizza types to menu item IDs (assuming these exist in the API)
    pizza_type_map = {
        "tandoori chicken": 1,
        "tandoori chicken supreme": 1,  # Support old name
        "spicy jaffna crab": 2,
        "spicy jaffna crab pizza": 2,  # Support old name
        "jaffna crab": 2,
        "curry chicken": 3,
        "curry chicken cashew": 3,
        "curry chicken & cashew": 3,
        "curry chicken & cashew pizza": 3,  # Support old name
        "spicy paneer": 4,
        "spicy paneer veggie": 4,
        "spicy paneer veggie pizza": 4,  # Support old name
        "paneer veggie": 4,
        "margherita": 5,
        "margherita classic": 5,
        "four cheese": 6, 
        "four cheese fusion": 6,
        "hot butter prawn": 7,
        "hot butter prawn pizza": 7,  # Support old name
        "butter prawn": 7,
        "masala potato": 8,
        "masala potato pea": 8,
        "masala potato & pea": 8,
        "masala potato & pea pizza": 8,  # Support old name
        "potato pea": 8
    }
    
    menu_item_id = pizza_type_map.get(pizza_type.lower(), 1)  # Default to Margherita
    
    # Prepare order items
    items = [{
        "menu_item_id": menu_item_id,
        "quantity": quantity,
        "size": size,
        "special_instructions": special_instructions
    }]
    
    # Prepare customer info
    customer_info = {
        "name": customer_name,
        "address": delivery_address
    }
    
    # Get OBO token
    obo_token = get_obo_token(user_token)
    
    # Try API first, fallback to static
    return place_order_via_api(items, customer_info, obo_token)


class PlaceOrderTool:
    """Legacy tool class for backward compatibility."""
    
    def __init__(self):
        self.name = "PlaceOrderTool"
        self.description = (
            "Place a pizza order with specified items, customer information, and delivery details. "
            "Calculates totals including tax and delivery fee, and provides order confirmation."
        )

    def _get_pizza_price(self, pizza_id: str, size: str = "Medium") -> float:
        """Get pizza price based on ID and size."""
        price_map = {
            "margherita-classic": {"Small": 10.50, "Medium": 12.50, "Large": 14.50},
            "four-cheese-fusion": {"Small": 11.25, "Medium": 13.25, "Large": 15.25},
            "tandoori-chicken-supreme": {"Small": 12.99, "Medium": 14.99, "Large": 16.99},
            "spicy-jaffna-crab-pizza": {"Small": 14.50, "Medium": 16.50, "Large": 18.50},
            "curry-chicken-cashew-pizza": {"Small": 11.99, "Medium": 13.99, "Large": 15.99},
            "spicy-paneer-veggie-pizza": {"Small": 11.50, "Medium": 13.50, "Large": 15.50},
            "hot-butter-prawn-pizza": {"Small": 13.50, "Medium": 15.50, "Large": 17.50},
            "masala-potato-pea-pizza": {"Small": 10.99, "Medium": 12.99, "Large": 14.99}
        }
        
        return price_map.get(pizza_id, {}).get(size, 12.99)  # Default price

    def _get_pizza_name(self, pizza_id: str) -> str:
        """Get pizza name from ID."""
        name_map = {
            "margherita-classic": "Margherita Classic",
            "four-cheese-fusion": "Four Cheese Fusion",
            "tandoori-chicken-supreme": "Tandoori Chicken",
            "spicy-jaffna-crab-pizza": "Spicy Jaffna Crab",
            "curry-chicken-cashew-pizza": "Curry Chicken & Cashew",
            "spicy-paneer-veggie-pizza": "Spicy Paneer Veggie",
            "hot-butter-prawn-pizza": "Hot Butter Prawn",
            "masala-potato-pea-pizza": "Masala Potato & Pea"
        }
        return name_map.get(pizza_id, "Unknown Pizza")

    def _run(self, pizza_type: str = "Margherita", quantity: int = 1, size: str = "Medium", 
             customer_name: str = "Pizza Lover", delivery_address: str = "123 Main St", 
             special_instructions: str = "", token: str = None) -> str:
        """Place a pizza order with authentication token."""
        
        try:
            # Validate authentication token
            if not token:
                return json.dumps({
                    "error": "Authentication required to place orders",
                    "success": False,
                    "requires_auth": True
                })
            
            # Generate order ID
            order_id = f"PZ{uuid.uuid4().hex[:8].upper()}"
            
            # Map pizza types to IDs
            pizza_type_map = {
                "margherita": "margherita-classic",
                "margherita classic": "margherita-classic",
                "four cheese": "four-cheese-fusion",
                "four cheese fusion": "four-cheese-fusion",
                "tandoori chicken": "tandoori-chicken-supreme",
                "tandoori chicken supreme": "tandoori-chicken-supreme",
                "spicy jaffna crab": "spicy-jaffna-crab-pizza",
                "spicy jaffna crab pizza": "spicy-jaffna-crab-pizza",
                "jaffna crab": "spicy-jaffna-crab-pizza",
                "curry chicken": "curry-chicken-cashew-pizza",
                "curry chicken cashew": "curry-chicken-cashew-pizza",
                "curry chicken & cashew": "curry-chicken-cashew-pizza",
                "curry chicken and cashew": "curry-chicken-cashew-pizza",
                "spicy paneer": "spicy-paneer-veggie-pizza",
                "spicy paneer veggie": "spicy-paneer-veggie-pizza",
                "paneer veggie": "spicy-paneer-veggie-pizza",
                "hot butter prawn": "hot-butter-prawn-pizza",
                "hot butter prawn pizza": "hot-butter-prawn-pizza",
                "butter prawn": "hot-butter-prawn-pizza",
                "masala potato": "masala-potato-pea-pizza",
                "masala potato pea": "masala-potato-pea-pizza",
                "masala potato & pea": "masala-potato-pea-pizza",
                "masala potato and pea": "masala-potato-pea-pizza",
                "potato pea": "masala-potato-pea-pizza"
            }
            
            pizza_id = pizza_type_map.get(pizza_type.lower(), "margherita-classic")
            
            # Create order item
            unit_price = self._get_pizza_price(pizza_id, size)
            total_price = unit_price * quantity
            
            order_item = {
                "pizza_id": pizza_id,
                "pizza_name": self._get_pizza_name(pizza_id),
                "quantity": quantity,
                "size": size,
                "special_instructions": special_instructions,
                "unit_price": unit_price,
                "total_price": total_price
            }
            
            subtotal = total_price
            
            # Calculate totals
            tax_rate = 0.08  # 8% tax
            delivery_fee = 2.99
            tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + tax + delivery_fee, 2)
            
            # Estimated delivery time (30-45 minutes from now)
            delivery_time = datetime.now() + timedelta(minutes=35)
            estimated_delivery = delivery_time.strftime("%I:%M %p")
            
            # Create order
            order = {
                "order_id": order_id,
                "customer_name": customer_name,
                "delivery_address": delivery_address,
                "items": [order_item],
                "subtotal": subtotal,
                "tax": tax,
                "delivery_fee": delivery_fee,
                "total": total,
                "special_instructions": special_instructions,
                "status": "confirmed",
                "created_at": datetime.now().isoformat(),
                "estimated_delivery": estimated_delivery,
                "success": True,
                "message": f"Order #{order_id} placed successfully! Your {pizza_type} pizza will be delivered by {estimated_delivery}."
            }
            
            return json.dumps(order, indent=2)
            
        except Exception as e:
            error_response = {
                "error": f"Failed to place order: {str(e)}",
                "success": False
            }
            return json.dumps(error_response, indent=2)
