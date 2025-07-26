from typing import List, Dict, Any
import json
import requests
import os
try:
    from crewai_tools import tool
except ImportError:
    try:
        from crewai.tools import tool
    except ImportError:
        from crewai.tools.base_tool import tool


class CalculateTotalTool:
    """Tool for calculating order totals."""
    
    def __init__(self):
        self.name = "CalculateTotalTool"
        self.description = (
            "Calculate the total cost for a pizza order including individual item prices, "
            "subtotal, tax, delivery fee, and any applicable discounts."
        )

    def _get_pizza_price(self, pizza_id: str, size: str = "Medium") -> float:
        """Get pizza price based on ID and size."""
        price_map = {
            "margherita-classic": {"Small": 8.99, "Medium": 10.99, "Large": 12.99},
            "four-cheese-deluxe": {"Small": 10.99, "Medium": 12.99, "Large": 14.99},
            "marinara-special": {"Small": 9.49, "Medium": 11.49, "Large": 13.49},
            "pepperoni-supreme": {"Small": 11.99, "Medium": 13.99, "Large": 15.99},
            "veggie-garden": {"Small": 9.99, "Medium": 11.99, "Large": 13.99}
        }
        
        return price_map.get(pizza_id, {}).get(size, 12.99)  # Default price

    def _get_pizza_name(self, pizza_id: str) -> str:
        """Get pizza name from ID."""
        name_map = {
            "margherita-classic": "Margherita Classic",
            "four-cheese-deluxe": "Four Cheese Deluxe",
            "marinara-special": "Marinara Special",
            "pepperoni-supreme": "Pepperoni Supreme",
            "veggie-garden": "Veggie Garden"
        }
        return name_map.get(pizza_id, "Unknown Pizza")

    def _apply_discount(self, subtotal: float, discount_code: str) -> tuple:
        """Apply discount code and return (discount_amount, discount_description)."""
        discount_codes = {
            "PIZZA10": (0.10, "10% off your order"),
            "WELCOME": (5.00, "$5 off your first order"),
            "STUDENT": (0.15, "15% student discount"),
            "FAMILY": (3.00, "$3 off orders over $25")
        }
        
        if not discount_code or discount_code not in discount_codes:
            return 0.0, ""
        
        discount_value, description = discount_codes[discount_code]
        
        if discount_code == "FAMILY" and subtotal < 25.00:
            return 0.0, "Family discount requires minimum $25 order"
        
        if discount_value < 1.0:  # Percentage discount
            discount_amount = subtotal * discount_value
        else:  # Fixed amount discount
            discount_amount = min(discount_value, subtotal)  # Don't exceed subtotal
        
        return round(discount_amount, 2), description

    def _run(self, items: List[Dict[str, Any]], include_delivery: bool = True, 
             discount_code: str = "") -> str:
        """Calculate order total."""
        
        try:
            # Process items and calculate subtotal
            item_details = []
            subtotal = 0.0
            
            for item in items:
                pizza_id = item.get("pizza_id", "")
                quantity = int(item.get("quantity", 1))
                size = item.get("size", "Medium")
                
                if not pizza_id:
                    return json.dumps({
                        "error": "Missing pizza_id in items",
                        "success": False
                    })
                
                unit_price = self._get_pizza_price(pizza_id, size)
                total_price = unit_price * quantity
                subtotal += total_price
                
                item_detail = {
                    "pizza_id": pizza_id,
                    "pizza_name": self._get_pizza_name(pizza_id),
                    "quantity": quantity,
                    "size": size,
                    "unit_price": unit_price,
                    "total_price": total_price
                }
                item_details.append(item_detail)
            
            # Apply discount if provided
            discount_amount, discount_description = self._apply_discount(subtotal, discount_code)
            discounted_subtotal = subtotal - discount_amount
            
            # Calculate tax and delivery
            tax_rate = 0.08  # 8% tax
            tax = round(discounted_subtotal * tax_rate, 2)
            delivery_fee = 2.99 if include_delivery else 0.0
            
            # Calculate final total
            total = round(discounted_subtotal + tax + delivery_fee, 2)
            
            # Create response
            calculation = {
                "items": item_details,
                "subtotal": round(subtotal, 2),
                "discount": {
                    "code": discount_code if discount_amount > 0 else "",
                    "amount": discount_amount,
                    "description": discount_description
                } if discount_amount > 0 else None,
                "discounted_subtotal": round(discounted_subtotal, 2),
                "tax": tax,
                "tax_rate": "8%",
                "delivery_fee": delivery_fee,
                "total": total,
                "savings": round(discount_amount, 2) if discount_amount > 0 else 0,
                "success": True
            }
            
            return json.dumps(calculation, indent=2)
            
        except Exception as e:
            error_response = {
                "error": f"Failed to calculate total: {str(e)}",
                "success": False
            }
            return json.dumps(error_response, indent=2)


@tool("Calculate Order Total")
def calculate_total_tool(items: List[Dict[str, Any]], include_delivery: bool = True, 
                        discount_code: str = "") -> str:
    """Calculate order total with pricing from API or fallback to static pricing."""
    
    # For now, use the existing static calculation logic
    # In a full implementation, this could call an API endpoint for dynamic pricing
    calculator = CalculateTotalTool()
    return calculator._run(items, include_delivery, discount_code)
