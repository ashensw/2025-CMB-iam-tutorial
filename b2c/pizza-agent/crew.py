import json
import logging
import os
import re
from datetime import date
from dotenv import load_dotenv
try:
    from crewai import Agent, Task, Crew, LLM, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI not available, falling back to rule-based responses")

from schemas import ChatResponse
from tools.get_menu import GetMenuTool, get_menu_tool
from tools.place_order import PlaceOrderTool
from tools.secure_place_order import SecurePlaceOrderTool
from tools.calculate_total import CalculateTotalTool, calculate_total_tool

load_dotenv()


class PizzaAssistant:
    """Pizza assistant with real AI integration."""
    
    def __init__(self, auth_manager=None):
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.auth_manager = auth_manager
        
        # Always use SecurePlaceOrderTool if we have Azure OpenAI configured (even in demo mode)
        # This ensures the auth requirement is triggered for order placement
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        use_secure_tool = api_key and api_key != "your_azure_openai_api_key_here"
        
        self.tools = {
            'get_menu': GetMenuTool(),
            'place_order': SecurePlaceOrderTool(auth_manager) if use_secure_tool else PlaceOrderTool(),
            'calculate_total': CalculateTotalTool()
        }
        
        if not self.demo_mode and CREWAI_AVAILABLE:
            self.setup_ai()
        else:
            logging.info("Running in demo mode with rule-based responses")
    
    def setup_ai(self):
        """Setup AI components."""
        try:
            # Check if Azure OpenAI credentials are available
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_API_BASE")
            deployment = os.getenv("AZURE_DEPLOYMENT_CHAT") or os.getenv("DEPLOYMENT_NAME")
            
            if not api_key or api_key == "your_azure_openai_api_key_here":
                logging.warning("Azure OpenAI API key not properly configured, falling back to demo mode")
                self.demo_mode = True
                return
                
            if not endpoint:
                logging.warning("Azure OpenAI endpoint not properly configured, falling back to demo mode")
                self.demo_mode = True
                return
            
            # Configure LLM with Azure OpenAI settings from B2B app
            model_config = f"azure/{deployment}" if deployment else "azure/gpt-4o-2024-11-20"
            self.llm = LLM(
                model=model_config,
                api_key=api_key,
                base_url=endpoint,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
            )
            
            logging.info(f"Azure OpenAI LLM initialized successfully with model: {model_config}")
            logging.info(f"Using endpoint: {endpoint}")
            
        except Exception as e:
            logging.error(f"Failed to initialize AI: {str(e)}")
            self.demo_mode = True

    def process_message(self, message: str, thread_id: str = None, obo_token: str = None) -> ChatResponse:
        """Process a user message and return appropriate response."""
        try:
            if self.demo_mode or not CREWAI_AVAILABLE:
                return self._process_with_rules(message, thread_id, obo_token)
            else:
                return self._process_with_ai(message, thread_id, obo_token)
                
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return ChatResponse(
                chat_response="I'm sorry, I'm having trouble processing your request right now. Please try asking about our pizza menu or placing an order! 🍕",
                tool_response=None,
                message_states=["error"]
            )
    
    def _process_with_ai(self, message: str, thread_id: str = None, obo_token: str = None) -> ChatResponse:
        """Process message using real AI (CrewAI)."""
        try:
            # Check if this is an order placement request - if so, delegate to rule-based system
            message_lower = message.lower()
            order_keywords = ['place order', 'place an order', 'order now', 'i want to order', 'place my order', 'order', 'buy', 'want', 'need', 'get me', 'i\'ll take']
            if any(keyword in message_lower for keyword in order_keywords):
                logging.info("Order detected in AI mode, delegating to rule-based system for order processing")
                return self._process_with_rules(message, thread_id, obo_token)
            # Create pizza specialist agent
            pizza_agent = Agent(
                role='Pizza Shop Assistant',
                goal=(
                    "Help customers with pizza orders, menu questions, and provide excellent customer service. "
                    "Use available tools to get accurate, real-time menu information and handle orders properly."
                ),
                backstory=(
                    "You are a friendly and knowledgeable Pizza Shack assistant. You love pizza and are passionate "
                    "about helping customers find the perfect meal. You have access to tools that can fetch the latest "
                    "menu information, calculate totals, and process orders. Always use these tools to provide "
                    "accurate information rather than relying on static data."
                ),
                verbose=True,
                llm=self.llm,
                tools=[get_menu_tool, calculate_total_tool],  # Enable menu and calculation tools with CrewAI compatibility
            )
            
            # Create task for the agent
            pizza_task = Task(
                description=f"""
                Customer message: {message}
                Current date: {date.today().isoformat()}
                
                # Pizza Shop Assistant Task
                
                ## Your Mission
                Help the customer with their pizza-related question or request using the available tools to provide accurate, real-time information.
                
                ## Available Tools
                1. **get_menu_tool** - Use this to fetch current menu items. You can filter by:
                   - category: 'vegetarian', 'classic', 'premium', 'specialty'
                   - price_range: 'budget', 'mid-range', 'premium'
                2. **calculate_total_tool** - Use this to calculate order totals with taxes and delivery
                
                ## Important Instructions
                
                ### For Menu Queries:
                - **ALWAYS** use the get_menu_tool to fetch real-time menu data
                - If customer asks about vegetarian/veggie/veg/plant-based options, use: get_menu_tool(category="vegetarian")
                - For general menu questions, use: get_menu_tool() to get all items
                - For price calculations, use the calculate_total_tool
                
                ### For Vegetarian Requests:
                When customer asks specifically about vegetarian, veggie, veg, or plant-based options:
                1. Use get_menu_tool(category="vegetarian") to get only vegetarian pizzas
                2. Present only the vegetarian options in a friendly way
                3. Don't show non-vegetarian pizzas unless specifically asked for the full menu
                
                ### Response Guidelines:
                1. Be friendly, enthusiastic about pizza, and use pizza emojis 🍕
                2. Use tools to get accurate information - don't guess or use static data
                3. Format responses nicely with pricing and descriptions
                4. Be conversational and engaging
                5. For ordering questions, be enthusiastic and direct customers to simply say what pizza they want (e.g., "I'll take a Tandoori Chicken") without needing to specify size
                6. **NEVER** generate image URLs or markdown image links - the frontend will handle images
                7. Present menu information in text format only with pricing and descriptions
                
                ## Customer Message Analysis
                Analyze what the customer is asking for and use the appropriate tools to provide accurate information.
                
                Please respond helpfully using the tools available to get real-time data.
                """,
                agent=pizza_agent,
                expected_output="A helpful and friendly response using real-time data from tools to answer the customer's pizza-related question."
            )
            
            # Create and execute crew
            pizza_crew = Crew(
                agents=[pizza_agent],
                tasks=[pizza_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = pizza_crew.kickoff()
            
            # Extract response from crew result
            if hasattr(result, 'raw'):
                response_text = result.raw
            else:
                response_text = str(result)
            
            return ChatResponse(
                chat_response=response_text,
                tool_response=None,
                message_states=["pizza_chat_active"]
            )
            
        except Exception as e:
            logging.error(f"AI processing failed: {str(e)}, falling back to rule-based")
            return self._process_with_rules(message, thread_id, obo_token)
    
    def _process_with_rules(self, message: str, thread_id: str = None, obo_token: str = None) -> ChatResponse:
        """Process message using rule-based logic (fallback/demo mode)."""
        try:
            # Analyze user intent
            intent = self._analyze_intent(message)
            logging.info(f"Intent analysis result: {intent}")
            
            # Execute appropriate tool or provide general response
            if intent['action'] == 'get_menu':
                tool_result = self._execute_tool('get_menu', intent.get('params', {}))
                response_text = self._format_menu_response(tool_result)
                tool_response = None
            elif intent['action'] == 'calculate_total':
                tool_result = self._execute_tool('calculate_total', intent.get('params', {}))
                response_text = self._format_calculation_response(tool_result)
                tool_response = None
            elif intent['action'] == 'place_order':
                order_info = intent.get('params', {})
                items = order_info.get('items', [])
                
                # Auto-assign Medium size for all items (no need to ask user for size)
                if items:
                    for item in items:
                        if not item.get('size'):
                            item['size'] = 'Medium'  # Default to Medium size for simplified ordering
                
                tool_result = self._execute_tool('place_order', order_info, obo_token)
                response_text = self._format_order_response(tool_result)
                # Parse tool_result as JSON if it's a string
                try:
                    tool_response = json.loads(tool_result) if isinstance(tool_result, str) else tool_result
                except json.JSONDecodeError:
                    tool_response = {"raw_response": tool_result}
            else:
                response_text = self._generate_general_response(message)
                tool_response = None
            
            return ChatResponse(
                chat_response=response_text,
                tool_response=tool_response,
                message_states=["pizza_chat_active"]
            )
            
        except Exception as e:
            logging.error(f"Rule-based processing failed: {str(e)}")
            return ChatResponse(
                chat_response="I'm sorry, I'm having trouble processing your request right now. Please try asking about our pizza menu or placing an order! 🍕",
                tool_response=None,
                message_states=["error"]
            )
    
    def _analyze_intent(self, message: str) -> dict:
        """Analyze user message to determine intent."""
        message_lower = message.lower()
        
        # Note: Size selection removed for simplified demo app
        # All pizzas now use standard medium size automatically
        
        # Order placement keywords (check first - most specific)
        # But exclude cases where user is asking about menu options
        is_menu_query = any(word in message_lower for word in ['menu', 'options', 'available', 'what do you have', 'show me', 'do you have'])
        if not is_menu_query and any(word in message_lower for word in ['order', 'buy', 'want', 'need', 'get me', 'i\'ll take', 'place order']):
            return {'action': 'place_order', 'params': self._extract_order_info(message)}
        
        # Price calculation keywords  
        if any(word in message_lower for word in ['total', 'cost', 'price', 'how much', 'calculate']):
            return {'action': 'calculate_total', 'params': self._extract_order_items(message)}
        
        # Menu-related keywords with category detection
        if any(word in message_lower for word in ['menu', 'pizza', 'what do you have', 'options', 'available']):
            # Check for specific category keywords
            menu_params = {}
            
            # Vegetarian keywords
            if any(word in message_lower for word in ['veg', 'vegetarian', 'veggie', 'vegi', 'plant-based', 'no meat']):
                menu_params['category'] = 'vegetarian'
            # Classic keywords
            elif any(word in message_lower for word in ['classic', 'traditional', 'margherita']):
                menu_params['category'] = 'classic'
            # Premium keywords
            elif any(word in message_lower for word in ['premium', 'cheese', 'four cheese']):
                menu_params['category'] = 'premium'
            # Specialty keywords
            elif any(word in message_lower for word in ['specialty', 'special', 'tandoori', 'crab', 'curry', 'sri Lankan', 'prawn']):
                menu_params['category'] = 'specialty'
            
            # Price range detection
            if any(word in message_lower for word in ['cheap', 'budget', 'affordable', 'under']):
                menu_params['price_range'] = 'budget'
            elif any(word in message_lower for word in ['expensive', 'premium price', 'over']):
                menu_params['price_range'] = 'premium'
            elif any(word in message_lower for word in ['mid range', 'medium price', 'average']):
                menu_params['price_range'] = 'mid-range'
            
            return {'action': 'get_menu', 'params': menu_params}
        
        return {'action': 'general', 'params': {}}
    
    def _extract_order_items(self, message: str) -> dict:
        """Extract order items from message for calculation."""
        items = []
        
        # Use more specific names to avoid partial matching issues
        pizza_map = {
            # Full names matching menu items
            'tandoori chicken': 'tandoori-chicken-supreme',
            'tandoori chicken supreme': 'tandoori-chicken-supreme',
            'spicy jaffna crab': 'spicy-jaffna-crab-pizza',
            'spicy jaffna crab pizza': 'spicy-jaffna-crab-pizza',
            'jaffna crab': 'spicy-jaffna-crab-pizza',
            'curry chicken cashew': 'curry-chicken-cashew-pizza',
            'curry chicken & cashew': 'curry-chicken-cashew-pizza',
            'curry chicken and cashew': 'curry-chicken-cashew-pizza',
            'curry chicken': 'curry-chicken-cashew-pizza',
            'spicy paneer veggie': 'spicy-paneer-veggie-pizza',
            'spicy paneer veggie pizza': 'spicy-paneer-veggie-pizza',
            'spicy paneer': 'spicy-paneer-veggie-pizza',
            'paneer veggie': 'spicy-paneer-veggie-pizza',
            'margherita classic': 'margherita-classic',
            'four cheese fusion': 'four-cheese-fusion',
            'four cheese': 'four-cheese-fusion',
            'hot butter prawn': 'hot-butter-prawn-pizza',
            'hot butter prawn pizza': 'hot-butter-prawn-pizza',
            'butter prawn': 'hot-butter-prawn-pizza',
            'masala potato pea': 'masala-potato-pea-pizza',
            'masala potato & pea': 'masala-potato-pea-pizza',
            'masala potato and pea': 'masala-potato-pea-pizza',
            'masala potato': 'masala-potato-pea-pizza',
            'potato pea': 'masala-potato-pea-pizza',
            # Add short names too for convenience
            'margherita': 'margherita-classic',
            'cheese': 'four-cheese-fusion',
            'tandoori': 'tandoori-chicken-supreme',
            'crab': 'spicy-jaffna-crab-pizza',
            'paneer': 'spicy-paneer-veggie-pizza',
            'prawn': 'hot-butter-prawn-pizza',
            'potato': 'masala-potato-pea-pizza'
        }
        
        # Sort keys by length (longest first) to match "margherita classic" before just "margherita"
        sorted_pizza_keys = sorted(pizza_map.keys(), key=len, reverse=True)
        
        message_lower = message.lower()
        processed_indices = set()
        
        for pizza_name in sorted_pizza_keys:
            for match in re.finditer(re.escape(pizza_name), message_lower):
                # Ensure we don't process a substring of an already matched longer pizza name
                if any(i in processed_indices for i in range(match.start(), match.end())):
                    continue
                
                pizza_id = pizza_map[pizza_name]
                
                # --- Size Extraction (now more precise) ---
                size = None
                # Define a closer context for size extraction
                pre_context = message_lower[max(0, match.start() - 10):match.start()]
                post_context = message_lower[match.end():match.end() + 10]

                # Check for size keywords in the immediate vicinity of the pizza name
                # Prefer the size mentioned *after* the pizza, as in "Tandoori Chicken Large"
                if 'large' in post_context or 'large' in pre_context:
                    size = "Large"
                elif 'medium' in post_context or 'medium' in pre_context:
                    size = "Medium"
                elif 'small' in post_context or 'small' in pre_context:
                    size = "Small"
                
                # Debug logging
                logging.info(f"SIZE DEBUG: pizza='{pizza_name}', pre_context='{pre_context}', post_context='{post_context}', detected_size='{size}'")

                # --- Quantity Extraction ---
                quantity = 1
                # Look for a number immediately before the pizza name
                pre_context = message_lower[max(0, match.start() - 5):match.start()]
                qty_match = re.search(r'(\d+)\s*$', pre_context)
                if qty_match:
                    quantity = int(qty_match.group(1))
                
                items.append({
                    'pizza_id': pizza_id,
                    'quantity': quantity,
                    'size': size  # This will be None if no size is found
                })
                
                # Mark this part of the string as processed
                for i in range(match.start(), match.end()):
                    processed_indices.add(i)

        # Deduplicate items in case short and long names match the same pizza
        # e.g., "curry chicken cashew" and "curry chicken"
        unique_items = []
        seen_pizza_ids = set()
        for item in items:
            if item['pizza_id'] not in seen_pizza_ids:
                unique_items.append(item)
                seen_pizza_ids.add(item['pizza_id'])
                
        return {'items': unique_items}
    
    def _extract_order_info(self, message: str) -> dict:
        """Extract order information from message."""
        order_items = self._extract_order_items(message)
        
        # In a real implementation, you'd extract customer info too
        return {
            'items': order_items.get('items', []),
            'customer_name': 'Customer',  # Would be extracted from auth context
            'delivery_address': '123 Main St',  # Would be prompted for
            'special_instructions': ''
        }
    
    def _execute_tool(self, tool_name: str, params: dict, obo_token: str = None) -> str:
        """Execute a tool with given parameters."""
        tool = self.tools.get(tool_name)
        if not tool:
            return json.dumps({"error": f"Tool {tool_name} not found"})
        
        try:
            if tool_name == 'get_menu':
                return tool._run(
                    category=params.get('category'),
                    price_range=params.get('price_range')
                )
            elif tool_name == 'calculate_total':
                return tool._run(
                    items=params.get('items', []),
                    include_delivery=params.get('include_delivery', True),
                    discount_code=params.get('discount_code', '')
                )
            elif tool_name == 'place_order':
                # Extract first item from items for order placement
                items = params.get('items', [])
                if not items:
                    return json.dumps({"error": "No items specified for order", "success": False})
                
                # For now, handle single item orders (first item only)
                first_item = items[0]
                pizza_type = first_item.get('pizza_id', 'margherita-classic').replace('-', ' ').title()
                
                # Check if this is a secure tool that needs auth
                if hasattr(tool, 'secure_tool'):
                    # SecurePlaceOrderTool - this tool handles auth internally and is async
                    # For now, return auth required to trigger the auth flow
                    # The actual order will be processed in the callback after auth
                    return json.dumps({
                        "error": "Authentication required to place orders",
                        "success": False,
                        "message": "Please log in to place your order. Click the 'Login to Order' button to authenticate with Asgardeo.",
                        "requires_auth": True
                    })
                else:
                    # Regular PlaceOrderTool - map pizza_id to pizza_type
                    pizza_type_map = {
                        'tandoori-chicken-supreme': 'Tandoori Chicken',
                        'spicy-jaffna-crab-pizza': 'Spicy Jaffna Crab',
                        'curry-chicken-cashew-pizza': 'Curry Chicken & Cashew',
                        'spicy-paneer-veggie-pizza': 'Spicy Paneer Veggie',
                        'margherita-classic': 'Margherita Classic',
                        'four-cheese-fusion': 'Four Cheese Fusion',
                        'hot-butter-prawn-pizza': 'Hot Butter Prawn',
                        'masala-potato-pea-pizza': 'Masala Potato & Pea'
                    }
                    pizza_type = pizza_type_map.get(first_item.get('pizza_id', 'margherita-classic'), 'Margherita Classic')
                    
                    actual_size = first_item.get('size') or 'Medium'
                    logging.info(f"TOOL DEBUG: pizza_type='{pizza_type}', extracted_size='{first_item.get('size')}', final_size='{actual_size}'")
                    
                    return tool._run(
                        pizza_type=pizza_type,
                        quantity=first_item.get('quantity', 1),
                        size=actual_size,  # Only default if size is None/empty
                        customer_name=params.get('customer_name', 'Customer'),
                        delivery_address=params.get('delivery_address', '123 Main St'),
                        special_instructions=params.get('special_instructions', '')
                    )
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _format_menu_response(self, tool_result: str) -> str:
        """Format menu tool result into user-friendly response."""
        try:
            data = json.loads(tool_result)
            if 'error' in data:
                return f"Sorry, I couldn't get the menu right now: {data['error']}"
            
            menu_items = data.get('menu_items', [])
            if not menu_items:
                return "I couldn't find any pizzas matching your criteria."
            
            response = "Here's our delicious pizza menu! 🍕 Let me know if you'd like recommendations or need help ordering.\n\n"
            
            # Group items by category for better presentation
            categories = {}
            for item in menu_items:
                category = item.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            # Define category display order and titles
            category_order = ['specialty', 'vegetarian', 'classic', 'premium']
            category_titles = {
                'specialty': '### Specialty Pizzas',
                'vegetarian': '### Vegetarian Pizzas', 
                'classic': '### Classic Pizza',
                'premium': '### Premium Pizza'
            }
            
            for category in category_order:
                if category in categories:
                    response += f"{category_titles[category]}\n"
                    for i, item in enumerate(categories[category], 1):
                        # Format price to always show 2 decimal places
                        price = f"{float(item['price']):.2f}"
                        response += f"{i}. {item['name']}\n"
                        response += f"Description: {item['description']}\n"
                        response += f"Price: ${price}\n"
                        if item.get('image_url'):
                            # Use the provided image_url from the menu data
                            response += f"![{item['name']}]({item['image_url']})\n"
                        response += "\n"
                    response += "---\n\n"
            
            response += "What would you like to order? Just let me know! 😊"
            return response
            
        except json.JSONDecodeError:
            return ("Here's our delicious pizza menu! 🍕\n\n"
                    "**Specialty Sri Lankan-Inspired:** Tandoori Chicken ($14.99), Spicy Jaffna Crab ($16.50), "
                    "Curry Chicken & Cashew ($13.99), Hot Butter Prawn ($15.50)\n\n"
                    "**Vegetarian:** Spicy Paneer Veggie ($13.50), Masala Potato & Pea ($12.99)\n\n"
                    "**Classics:** Margherita Classic ($12.50), Four Cheese Fusion ($13.25)\n\n"
                    "What would you like to order?")
    
    def _format_calculation_response(self, tool_result: str) -> str:
        """Format calculation tool result into user-friendly response."""
        try:
            data = json.loads(tool_result)
            if 'error' in data:
                return f"Sorry, I couldn't calculate that: {data['error']}"
            
            response = "💰 **Order Total** 💰\n\n"
            
            for item in data.get('items', []):
                response += f"{item['quantity']}x {item['pizza_name']} ({item['size']}) - ${item['total_price']:.2f}\n"
            
            response += f"\nSubtotal: ${data.get('subtotal', 0):.2f}\n"
            response += f"Tax (8%): ${data.get('tax', 0):.2f}\n"
            response += f"Delivery: ${data.get('delivery_fee', 0):.2f}\n"
            
            if data.get('discount'):
                response += f"Discount: -${data['discount']['amount']:.2f}\n"
            
            response += f"\n**Total: ${data.get('total', 0):.2f}**\n\n"
            response += "Would you like to place this order? 🛒"
            
            return response
            
        except json.JSONDecodeError:
            return "I can help you calculate order totals! Just tell me which pizzas and quantities you'd like."
    
    def _format_order_response(self, tool_result: str) -> str:
        """Format order tool result into user-friendly response."""
        try:
            data = json.loads(tool_result)
            if 'error' in data:
                # Don't show auth error messages - they're handled by the frontend
                if data.get('requires_auth') or 'Authentication required' in data.get('error', ''):
                    return ""  # Empty response, auth flow is handled elsewhere
                return f"Sorry, I couldn't place your order: {data['error']}"
            
            if not data.get('success'):
                return "There was an issue placing your order. Please try again."
            
            response = "🎉 **Order Confirmed!** 🎉\n\n"
            response += f"📋 **Order ID**: {data.get('order_id')}\n\n"
            
            # Add pizza details
            response += "🍕 **Your Order**:\n"
            for item in data.get('items', []):
                response += f"  • {item.get('quantity', 1)}x {item.get('pizza_name', 'Pizza')} ({item.get('size', 'Medium')})\n"
                if item.get('special_instructions'):
                    response += f"    📝 Special: {item['special_instructions']}\n"
            
            response += f"\n💰 **Total**: ${data.get('total'):.2f}\n"
            response += f"🕐 **Estimated Delivery**: {data.get('estimated_delivery')}\n"
            response += f"📍 **Delivery Address**: {data.get('delivery_address', 'Your address')}\n\n"
            response += "🚚 Your delicious pizza is being prepared and will be delivered hot and fresh!"
            
            return response
            
        except json.JSONDecodeError:
            return "Your order has been placed! Thank you for choosing Pizza Shack! 🍕"
    
    def _generate_general_response(self, message: str) -> str:
        """Generate a general response for non-specific queries."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        message_lower = message.lower().strip()
        
        if any(greeting in message_lower for greeting in greetings):
            return "Hello! 🍕 Welcome to Pizza Shack! I'm your AI assistant. I can help you with:\n\n• View our pizza menu\n• Calculate order totals\n• Place pizza orders\n\nWhat would you like to do today?"
        
        # Simplified ordering - no size selection needed
        if message_lower in ['small', 'medium', 'large']:
            return "Thanks! All our pizzas come in a perfect standard size. Just let me know which pizza you'd like to order. For example: 'I'll take a Tandoori Chicken' or 'Order Margherita Classic'."
        
        return "I'm here to help you with our delicious pizza menu and orders! You can ask me about:\n\n🍕 Our pizza menu and ingredients\n💰 Price calculations\n🛒 Placing orders\n\nWhat would you like to know?"


def process_pizza_chat(message: str, thread_id: str = None, auth_manager=None, obo_token: str = None) -> ChatResponse:
    """Process a pizza chat message and return response."""
    assistant = PizzaAssistant(auth_manager)
    return assistant.process_message(message, thread_id, obo_token)
