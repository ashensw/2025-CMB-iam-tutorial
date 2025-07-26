"""
Secure wrapper for place order tool that requires authentication
"""

from typing import List, Dict, Any
import logging
from sdk.auth import SecureFunctionTool, AuthSchema, PizzaAuthManager, AuthConfig, OAuthTokenType
from tools.place_order import PlaceOrderTool


class SecurePlaceOrderTool:
    """Secure version of PlaceOrderTool that requires OBO authentication."""
    
    def __init__(self, auth_manager: PizzaAuthManager):
        self.name = "SecurePlaceOrderTool"
        self.description = (
            "Place a pizza order with authentication. Requires user to be logged in via Asgardeo. "
            "Calculates totals including tax and delivery fee, and provides order confirmation."
        )
        
        # Create auth config for order placement with IETF draft compliance
        auth_config = AuthConfig(
            scopes=["openid", "profile", "pizza:order"],
            token_type=OAuthTokenType.OBO_TOKEN,
            resource="pizza_api"
        )
        
        # Create auth schema
        auth_schema = AuthSchema(auth_manager, auth_config)
        
        # Create secure tool wrapper
        base_tool = PlaceOrderTool()
        self.secure_tool = SecureFunctionTool(base_tool, auth_manager, auth_config)
        
        self.logger = logging.getLogger(__name__)
    
    async def _run(self, items: List[Dict[str, Any]], customer_name: str, 
                   delivery_address: str, special_instructions: str = "") -> str:
        """Place a pizza order with authentication check."""
        try:
            self.logger.info(f"Attempting to place order for customer: {customer_name}")
            
            # Execute with authentication
            result = await self.secure_tool.execute(
                items=items,
                customer_name=customer_name,
                delivery_address=delivery_address,
                special_instructions=special_instructions
            )
            
            self.logger.info("Order placed successfully with authentication")
            return result
            
        except Exception as e:
            self.logger.error(f"Secure order placement failed: {str(e)}")
            
            # Return user-friendly error message
            if "Authentication required" in str(e):
                return """
                {
                    "error": "Authentication required to place orders",
                    "success": false,
                    "message": "Please log in to place your order. Click the 'Login to Order' button to authenticate with Asgardeo.",
                    "requires_auth": true
                }
                """
            else:
                return f"""
                {{
                    "error": "Order placement failed: {str(e)}",
                    "success": false
                }}
                """
    
    def __getattr__(self, name):
        """Delegate other attributes to the base tool."""
        return getattr(self.secure_tool.tool, name)