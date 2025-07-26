"""
Secure Pizza Function Tools following the Hotel Agent pattern
Enhanced with WSO2 IAM authentication integration
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from sdk.auth import SecureFunctionTool, AuthSchema, AuthConfig, OAuthTokenType, OAuthToken
from tools.get_menu import get_menu_data
from tools.place_order import PlaceOrderTool
from tools.calculate_total import CalculateTotalTool

logger = logging.getLogger(__name__)

# Pizza API base URL (can be configured via environment)
PIZZA_API_BASE_URL = os.getenv("PIZZA_API_BASE_URL", "http://localhost:8002")


async def fetch_pizza_menu(token: OAuthToken, category: Optional[str] = None, price_range: Optional[str] = None) -> dict:
    """
    Fetch pizza menu using authenticated API call.
    This function will be wrapped with SecureFunctionTool.
    """
    logger.info(f"Fetching pizza menu with token: {token.access_token[:10]}...")
    
    try:
        # For now, use the existing static menu data
        # In production, this would make authenticated API calls
        menu_json = get_menu_data(category, price_range)
        menu_data = json.loads(menu_json)
        
        logger.info(f"Successfully fetched menu with {len(menu_data.get('menu_items', []))} items")
        return menu_data
        
    except Exception as e:
        logger.error(f"Error fetching menu: {e}")
        raise Exception(f"Failed to fetch menu: {str(e)}")


async def calculate_pizza_total(token: OAuthToken, items: List[Dict[str, Any]], 
                               discount_code: Optional[str] = None) -> dict:
    """
    Calculate pizza order total using authenticated API call.
    This function will be wrapped with SecureFunctionTool.
    """
    logger.info(f"Calculating total for {len(items)} items with token: {token.access_token[:10]}...")
    
    try:
        # Use the existing calculator tool
        calculator = CalculateTotalTool()
        result_json = calculator._run(items=items, discount_code=discount_code)
        result_data = json.loads(result_json)
        
        logger.info(f"Successfully calculated total: ${result_data.get('total', 0)}")
        return result_data
        
    except Exception as e:
        logger.error(f"Error calculating total: {e}")
        raise Exception(f"Failed to calculate total: {str(e)}")


async def place_pizza_order(token: OAuthToken, items: List[Dict[str, Any]], 
                           customer_name: str, delivery_address: str,
                           special_instructions: str = "") -> dict:
    """
    Place a pizza order using authenticated API call with OBO token.
    This function will be wrapped with SecureFunctionTool.
    """
    logger.info(f"Placing order for {customer_name} with token: {token.access_token[:10]}...")
    
    try:
        # Use the existing place order tool
        order_tool = PlaceOrderTool()
        
        # Extract first item for compatibility with existing tool
        if items and len(items) > 0:
            first_item = items[0]
            pizza_type = first_item.get('pizza_id', 'margherita-classic')
            quantity = first_item.get('quantity', 1)
            size = first_item.get('size', 'Medium')
        else:
            raise ValueError("No items provided for order")
        
        result_json = order_tool._run(
            pizza_type=pizza_type,
            quantity=quantity,
            size=size,
            customer_name=customer_name,
            delivery_address=delivery_address,
            special_instructions=special_instructions,
            token=token.access_token
        )
        
        result_data = json.loads(result_json)
        logger.info(f"Successfully placed order: {result_data.get('order_id', 'Unknown')}")
        return result_data
        
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise Exception(f"Failed to place order: {str(e)}")


def create_secure_pizza_tools(auth_manager):
    """
    Create secure function tools for pizza operations following the Hotel Agent pattern.
    
    Args:
        auth_manager: PizzaAuthManager instance for handling authentication
        
    Returns:
        tuple: (get_menu_tool, calculate_total_tool, place_order_tool)
    """
    
    # 1. Get Menu Tool - Uses AGENT_TOKEN (no user consent required)
    get_menu_tool = SecureFunctionTool(
        fetch_pizza_menu,
        description="Fetch the pizza menu with categories, prices, and detailed information about available pizzas",
        name="GetPizzaMenuTool",
        auth=AuthSchema(auth_manager, AuthConfig(
            scopes=["read_menu"],
            token_type=OAuthTokenType.AGENT_TOKEN,
            resource="pizza_api"
        )),
        strict=True
    )
    
    # 2. Calculate Total Tool - Uses AGENT_TOKEN (no user consent required)
    calculate_total_tool = SecureFunctionTool(
        calculate_pizza_total,
        description="Calculate the total cost for a pizza order including tax, delivery fee, and any applicable discounts",
        name="CalculatePizzaTotalTool", 
        auth=AuthSchema(auth_manager, AuthConfig(
            scopes=["calculate_pricing"],
            token_type=OAuthTokenType.AGENT_TOKEN,
            resource="pizza_api"
        )),
        strict=True
    )
    
    # 3. Place Order Tool - Uses OBO_TOKEN (requires user consent)
    place_order_tool = SecureFunctionTool(
        place_pizza_order,
        description="Place a pizza order for the authenticated user. Requires user login and consent.",
        name="PlacePizzaOrderTool",
        auth=AuthSchema(auth_manager, AuthConfig(
            scopes=["create_orders", "openid", "profile"],
            token_type=OAuthTokenType.OBO_TOKEN,  # Requires user authentication
            resource="pizza_api"
        )),
        strict=True
    )
    
    logger.info("Created secure pizza tools: GetMenu, CalculateTotal, PlaceOrder")
    return get_menu_tool, calculate_total_tool, place_order_tool
