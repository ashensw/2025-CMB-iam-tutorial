from typing import Optional
import json
import requests
import os
from crewai.tools import tool


def get_agent_token() -> str:
    """Get agent token for API authentication (placeholder - implement with real Asgardeo)"""
    # In production, this would call Asgardeo to get a real agent token
    # For demo purposes, return a mock token
    return "demo-agent-token-for-menu-access"


def get_menu_data_from_api(category: Optional[str] = None, price_range: Optional[str] = None, auth_token: Optional[str] = None) -> str:
    """Get menu data from Pizza Shack API with JWT authentication"""
    
    api_base_url = os.getenv("PIZZA_API_URL", "http://localhost:8000")
    api_url = f"{api_base_url}/api/menu"
    
    # Prepare query parameters
    params = {}
    if category:
        params['category'] = category
    if price_range:
        params['price_range'] = price_range
    
    # Prepare headers with JWT token
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Add Authorization header if token is provided
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
        print(f"🔑 Using JWT token for menu API call")
    else:
        # Try to get agent token if none provided
        try:
            agent_token = get_agent_token()
            if agent_token and agent_token != "demo-agent-token-for-menu-access":
                headers['Authorization'] = f'Bearer {agent_token}'
                print(f"🔑 Using agent token for menu API call")
        except Exception as e:
            print(f"⚠️ Could not get agent token: {e}")
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        menu_items = response.json()
        
        # Format response to match frontend display (single price only)
        # Remove size_options to keep it simple for demo app
        simplified_items = []
        for item in menu_items:
            simplified_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "price": item.get("price"),  # Only medium price
                "category": item.get("category"),
                "image_url": item.get("image_url"),
                "ingredients": item.get("ingredients", [])
                # Removed size_options to match frontend
            }
            simplified_items.append(simplified_item)
        
        formatted_response = {
            "menu_items": simplified_items,
            "total_items": len(simplified_items),
            "categories": ["classic", "premium", "vegetarian", "specialty"],
            "price_ranges": ["budget (≤$13.00)", "mid-range ($13.00-$15.00)", "premium (>$15.00)"],
            "api_source": "pizza-shack-api"
        }
        
        return json.dumps(formatted_response, indent=2)
        
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}, falling back to static data")
        return get_static_menu_data(category, price_range)
    except Exception as e:
        print(f"Unexpected error: {e}, falling back to static data")
        return get_static_menu_data(category, price_range)


def get_static_menu_data(category: Optional[str] = None, price_range: Optional[str] = None) -> str:
    """Fallback static menu data when API is unavailable"""
    
    # Static pizza menu data (fallback) - simplified for demo app
    menu_items = [
        {
            "id": "tandoori-chicken-supreme",
            "name": "Tandoori Chicken",
            "description": "Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce",
            "price": 14.99,
            "image_url": "/images/tandoori_chicken.jpeg",
            "ingredients": ["Tandoori chicken", "Bell peppers", "Red onions", "Mozzarella cheese", "Spiced tomato sauce", "Indian herbs"],
            "category": "specialty"
        },
        {
            "id": "spicy-jaffna-crab-pizza",
            "name": "Spicy Jaffna Crab",
            "description": "Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!",
            "price": 16.50,
            "image_url": "/images/spicy_jaffna_crab.jpeg",
            "ingredients": ["Jaffna crab curry", "Mozzarella cheese", "Red onions", "Chili flakes", "Curry leaves", "Coconut milk base"],
            "category": "specialty"
        },
        {
            "id": "curry-chicken-cashew-pizza",
            "name": "Curry Chicken & Cashew",
            "description": "Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!",
            "price": 13.99,
            "image_url": "/images/curry_chicken_cashew.jpeg",
            "ingredients": ["Sri Lankan chicken curry", "Roasted cashews", "Mozzarella cheese", "Curry sauce", "Fresh coriander"],
            "category": "specialty"
        },
        {
            "id": "spicy-paneer-veggie-pizza",
            "name": "Spicy Paneer Veggie",
            "description": "Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella",
            "price": 13.50,
            "image_url": "/images/spicy_paneer_veggie.jpeg",
            "ingredients": ["Marinated paneer", "Bell peppers", "Red onions", "Tomatoes", "Mozzarella cheese", "Spiced tomato base"],
            "category": "vegetarian"
        },
        {
            "id": "margherita-classic",
            "name": "Margherita Classic",
            "description": "Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves",
            "price": 12.50,
            "image_url": "/images/margherita_classic.jpeg",
            "ingredients": ["Fresh mozzarella", "San Marzano tomato sauce", "Whole basil leaves", "Extra virgin olive oil", "Sea salt"],
            "category": "classic"
        },
        {
            "id": "four-cheese-fusion",
            "name": "Four Cheese Fusion",
            "description": "A cheese lover's dream with mozzarella, sharp cheddar, Parmesan, and creamy ricotta.",
            "price": 13.25,
            "image_url": "/images/four_cheese_fusion.jpeg",
            "ingredients": ["Mozzarella", "Sharp cheddar", "Parmesan", "Creamy ricotta", "Artisan crust", "Olive oil"],
            "category": "premium"
        },
        {
            "id": "hot-butter-prawn-pizza",
            "name": "Hot Butter Prawn",
            "description": "Juicy prawns in signature hot butter sauce with mozzarella and spring onions.",
            "price": 15.50,
            "image_url": "/images/hot_butter_prawn.jpeg",
            "ingredients": ["Juicy prawns", "Hot butter sauce", "Mozzarella cheese", "Spring onions", "Garlic", "Chili flakes"],
            "category": "specialty"
        },
        {
            "id": "masala-potato-pea-pizza",
            "name": "Masala Potato & Pea",
            "description": "Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella",
            "price": 12.99,
            "image_url": "/images/masala_potato_pea.jpeg",
            "ingredients": ["Spiced potatoes", "Green peas", "Mozzarella cheese", "Masala spices", "Fresh coriander", "Cumin"],
            "category": "vegetarian"
        }
    ]
    
    # Filter by category if specified
    if category:
        category_lower = category.lower()
        menu_items = [item for item in menu_items if item["category"] == category_lower]
    
    # Filter by price range if specified
    if price_range:
        price_range_lower = price_range.lower()
        if price_range_lower == "budget":
            menu_items = [item for item in menu_items if item["price"] <= 13.00]
        elif price_range_lower == "mid-range":
            menu_items = [item for item in menu_items if 13.00 < item["price"] <= 15.00]
        elif price_range_lower == "premium":
            menu_items = [item for item in menu_items if item["price"] > 15.00]
    
    if not menu_items:
        return "No pizzas found matching your criteria. Please try different filters."
    
    # Format the response
    response = {
        "menu_items": menu_items,
        "total_items": len(menu_items),
        "categories": ["classic", "premium", "vegetarian", "specialty"],  
        "price_ranges": ["budget (≤$13.00)", "mid-range ($13.00-$15.00)", "premium (>$15.00)"],
        "api_source": "static-fallback"
    }
    
    return json.dumps(response, indent=2)


def get_menu_data(category: Optional[str] = None, price_range: Optional[str] = None, auth_token: Optional[str] = None) -> str:
    """Get menu data - try API first, fallback to static data"""
    return get_menu_data_from_api(category, price_range, auth_token)


@tool("Get Pizza Menu")
def get_menu_tool(category: Optional[str] = None, price_range: Optional[str] = None, auth_token: Optional[str] = None) -> str:
    """Get the complete pizza menu or filter by category and price range. Returns detailed information about available pizzas including prices, ingredients, and descriptions.
    
    Args:
        category: Filter by pizza category (classic, premium, vegetarian, specialty)
        price_range: Filter by price range (budget, mid-range, premium)
        auth_token: JWT token for authenticated API access
    """
    return get_menu_data(category, price_range, auth_token)


# Keep the old class for backward compatibility
class GetMenuTool:
    """Legacy tool class for backward compatibility."""
    
    def __init__(self):
        self.name = "GetMenuTool"
        self.description = (
            "Get the complete pizza menu or filter by category and price range. "
            "Returns detailed information about available pizzas including prices, ingredients, and descriptions."
        )

    def _run(self, category: Optional[str] = None, price_range: Optional[str] = None, auth_token: Optional[str] = None) -> str:
        """Get pizza menu with optional filtering and JWT authentication."""
        return get_menu_data(category, price_range, auth_token)