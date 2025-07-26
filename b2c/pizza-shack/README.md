# Pizza Shack - B2C Tutorial Application

A modern React-based pizza ordering application showcasing **personalized recommendations** and **conversational AI ordering** with guest user support powered by Customer Data Platform (CDP) integration.

## ✨ Core Features

This demo app highlights two main capabilities:

### 🌟 **Personalized Recommendations**
- **Profile ID Tracking**: Guest orders create persistent profile IDs stored in browser
- **Cross-Session Persistence**: Order history tracked even before account creation
- **Smart Recommendations**: "⭐ Your Personalized Picks" section shows past favorites
- **Accurate Messaging**: "🧡 YOU LOVED THIS BEFORE!" badges on previously ordered items
- **Contextual Copy**: "Suggested based on your recent choices. Kept just for you!"
- **Guest→Login Flow**: Seamless transition from guest ordering to authenticated personalization

### 🤖 **Conversational AI Assistant**
- **Personalization-Aware Chat**: AI welcome message mentions access to taste preferences
- **Pre-populated Queries**: Suggestion chips auto-fill chat input with relevant prompts
- **Enhanced Prompt Bar**: Interactive suggestion chips above personalized picks section
- **WebSocket Real-time**: Live bidirectional communication for seamless ordering
- **Context-Aware Responses**: AI references user's past orders and preferences in conversations

### 🛒 **Additional Features**
- **Interactive Pizza Menu** - Browse and order from 8 curated Sri Lankan-inspired pizzas
- **Smart Shopping Cart** - Real-time totals with quantity controls
- **Dual User Experience** - Full support for both authenticated and guest users
- **Asgardeo Authentication** - Secure SSO with modern UI components
- **Past Orders History** - View previous orders with creator identification

### 🎯 **Demo-Ready Design**
- **Warm Pizza Theme** - Tomato red, basil green, and mozzarella cream colors
- **Smooth Animations** - Fade-in effects and micro-interactions
- **Responsive Layout** - Optimized for desktop demo and mobile viewing
- **Professional Polish** - Modern shadows, typography, and visual hierarchy

### 📋 Past Orders Feature

- **Order History**: View all past orders with detailed information
- **Creator Detection**: Distinguish orders placed by user vs AI agent
- **JWT Token Analysis**: Detects `act` claim to identify AI agent orders
- **Visual Indicators**: Color-coded badges showing order creator
- **Filtering Options**: Filter by All Orders, My Orders, or AI Agent Orders
- **Order Details**: Shows items, quantities, prices, timestamps, and status

## Pizza Menu

Our curated pizza selection features 8 carefully crafted pizzas with authentic flavors:

### Current Menu (8 Pizzas)

| **Pizza**                        | **Description**                                                                                              | **Price** | **Category** |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------- | ------------------ |
| **Margherita Classic**           | Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves                   | $12.50          | Classic            |
| **Four Cheese Fusion**           | Cheese lover's dream! Blend of mozzarella, sharp cheddar, Parmesan, and creamy ricotta on artisan crust            | $13.25          | Premium            |
| **Tandoori Chicken Supreme**     | Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce                                           | $14.99          | Specialty          |
| **Spicy Jaffna Crab Pizza**      | Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!                          | $16.50          | Specialty          |
| **Curry Chicken & Cashew Pizza** | Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!                                      | $13.99          | Specialty          |
| **Spicy Paneer Veggie Pizza**    | Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella                          | $13.50          | Vegetarian         |
| **Hot Butter Prawn Pizza**       | Beloved Sri Lankan dish! Juicy prawns in hot butter sauce, mozzarella, fresh spring onions. Deliciously addictive! | $15.50          | Specialty          |
| **Masala Potato & Pea Pizza**    | Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella                               | $12.99          | Vegetarian         |

### Image Requirements

All pizza images must be in **1:1 square ratio** format for consistent display across the application. The layout uses `object-fit: cover` to properly display square images without distortion.

**Supported formats:** JPG, PNG, WebP
**Recommended dimensions:** 400x400px minimum
**Location:** `/public/images/`

## Technology Stack

- **Frontend**: React 19, Vite
- **Authentication**: Asgardeo React SDK v0.5.12
- **Design System**: Modern CSS with design tokens and Inter font
- **Styling**: CSS variables with warm orange-amber palette
- **AI Integration**: CrewAI WebSocket service
- **Customer Data Platform**: Choreo CDP REST API
- **Storage**: Browser localStorage with fallback support

#### New SDK Features

- **Built-in Components**: `SignedIn`, `SignedOut`, `SignInButton`, `UserDropdown`
- **Simplified Configuration**: Direct props instead of config objects
- **Enhanced UI**: Modern, accessible authentication components
- **Better TypeScript Support**: Improved type definitions and IntelliSense

#### Authentication UI Components

- **SignedIn/SignedOut**: Conditional rendering based on authentication state
- **SignInButton**: Customizable login button with render props pattern
- **UserDropdown**: Built-in user menu with account management and logout
- **Automatic Redirects**: Handled internally by the SDK

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ (for AI chat backend)

### Installation

1. **Clone and navigate to the project:**

   ```bash
   cd b2c/tutorial-app/pizza-shack
   ```
2. **Install dependencies:**

   ```bash
   npm install
   ```
3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file with your configuration.
4. **Start the application:**

   ```bash
   # Use automated scripts (recommended)
   cd ../
   ./start_services.sh

   # Or start manually
   npm run dev  # Frontend on http://localhost:5173
   ```

### Service Management

**Quick Commands:**

```bash
# Start all services (frontend + backend)
./start_services.sh

# Stop all services  
./stop_services.sh

# View logs
tail -f logs/frontend.log
tail -f logs/backend.log
```

**Manual Service Control:**

```bash
# Frontend only
npm run dev

# Check service status
lsof -i :5173  # Frontend
lsof -i :8001  # Backend
```

## CDP Integration

### API Endpoints

**Create Guest Profile:**

```http
POST https://bcef7ba7-0af4-40f4-b2ad-9089f700803c-dev.e1-us-east-azure.choreoapis.dev/default/iam-cdm/v1.0/profiles

Content-Type: application/json

{
  "identity_attributes": {
    "email": "guest@example.com",
    "displayName": "John Doe",
    "mobile": "1234567890"
  },
  "profile_id": "guest_1641234567890_abc123",
  "traits": {
    "orderer": {
      "order_1": {
        "PizzaType": "Margherita Classic",
        "size": "medium",
        "quantity": "2",
        "price": "$10.99"
      }
    }
  }
}
```

**Retrieve Profile:**

```http
GET https://bcef7ba7-0af4-40f4-b2ad-9089f700803c-dev.e1-us-east-azure.choreoapis.dev/default/iam-cdm/v1.0/profiles/{profile_id}
```

### Profile ID Management

**Storage Strategy:**

- Primary: localStorage (persistent across browser sessions)
- Fallback: sessionStorage (current session only)
- Last resort: In-memory storage

**Profile ID Format:**

```
guest_{timestamp}_{random_string}
Example: guest_1641234567890_abc123
```

**Security Features:**

- Automatic expiration (default: 90 days)
- Expired profile cleanup on app start
- Graceful degradation when storage is unavailable
- No sensitive data stored in profile ID

## Configuration

### Environment Variables

Create a `.env` file with the following options:

```bash
# CDP Feature Toggle
VITE_CDP_ENABLED=true

# CDP API Configuration (optional override)
VITE_CDP_BASE_URL=https://your-cdp-endpoint.com/v1.0

# Profile Storage Settings
VITE_PROFILE_EXPIRY_DAYS=90

# Debug Mode
VITE_CDP_DEBUG=false
```

### Feature Configuration

**Enable/Disable CDP:**

```javascript
// Set VITE_CDP_ENABLED=false to disable all CDP features
// App will continue to work normally without personalization
```

**Custom CDP Endpoint:**

```javascript
// Override default CDP URL
VITE_CDP_BASE_URL=https://your-custom-endpoint.com/v1.0
```

## Development

### Project Structure

```
src/
├── components/
│   ├── EnhancedChatBot.jsx      # AI chat integration
│   ├── PersonalizedRecommendations.jsx  # CDP recommendations UI
│   └── MyOrders.jsx             # Past orders with creator detection
├── services/
│   └── cdpService.js            # CDP API communication layer
├── utils/
│   └── profileStorage.js        # Secure browser storage utilities
├── App.jsx                      # Main application component
└── main.jsx                     # Application entry point
```

### Key Components

**CDPService (`src/services/cdpService.js`)**

- Handles all CDP API communication
- Graceful error handling with timeouts
- Environment-based configuration
- Profile data formatting and validation

**ProfileStorage (`src/utils/profileStorage.js`)**

- Secure browser storage management
- Multiple storage fallback strategy
- Automatic expiration handling
- Storage availability detection

**PersonalizedRecommendations (`src/components/PersonalizedRecommendations.jsx`)**

- Displays "You may like" suggestions
- Matches previous orders to current menu
- Seamless integration with existing UI patterns

**MyOrders (`src/components/MyOrders.jsx`)**

- Displays user's past order history
- Differentiates orders created by user vs AI agent
- Filters orders by creator type (All/User/Agent)
- Shows order details, timestamps, and status

### Error Handling & Fallbacks

**Graceful Degradation:**

- CDP service failures don't affect core ordering functionality
- Storage unavailability falls back to memory storage
- Network timeouts (10s for create, 8s for retrieve) prevent hanging
- Invalid profiles are automatically cleaned up

**Fallback Scenarios:**

1. **CDP Service Down**: Orders complete normally, no personalization
2. **Storage Unavailable**: Falls back to sessionStorage then memory
3. **Profile Not Found**: Removes invalid profile ID, starts fresh
4. **Network Timeout**: Continues without CDP features

### Adding New Pizzas

To add new pizzas to the menu, follow these steps to ensure consistency across all application layers:

#### 1. Update Database & API (`/b2c/pizza-api/main.py`)

Add the new pizza to the `menu_items` array:

```python
{
    "name": "Your New Pizza",
    "description": "Delicious description here",
    "price": 14.99,
    "category": "specialty",  # classic, premium, vegetarian, specialty
    "image_url": "/images/your-new-pizza.jpg",
    "ingredients": ["Ingredient 1", "Ingredient 2", "Ingredient 3"],
    "size_options": ["Small ($12.99)", "Medium ($14.99)", "Large ($16.99)"]
}
```

#### 2. Update Frontend Menu (`/b2c/pizza-shack/src/App.jsx`)

Add to the `pizzaMenu` array and update `getMenuItemId` mapping:

```javascript
// Add to pizzaMenu array
{
  name: "Your New Pizza",
  description: "Delicious description here",
  price: "$14.99",
  image: "/images/your-new-pizza.jpg",
  category: "specialty"
}

// Update getMenuItemId function
const getMenuItemId = (itemName) => {
  const menuNameToIdMap = {
    // ... existing mappings
    'Your New Pizza': 9,  // Next available ID
  };
  return menuNameToIdMap[itemName] || 1;
};
```

#### 3. Update AI Agent Knowledge

**Menu Tool (`/b2c/pizza-agent/tools/get_menu.py`):**
Add to the `menu_items` array in `get_static_menu_data()`:

```python
{
    "id": "your-new-pizza",
    "name": "Your New Pizza", 
    "description": "Delicious description here",
    "price": 14.99,
    "category": "specialty"
    # ... other fields
}
```

**Order Tool (`/b2c/pizza-agent/tools/place_order.py`):**
Update the `pizza_type_map` in both functions:

```python
pizza_type_map = {
    # ... existing mappings
    "your new pizza": 9,
    "new pizza": 9,
}
```

#### 4. Add Pizza Image

1. **Create/source a 1:1 square ratio image (400x400px minimum)**
2. **Save as:** `/b2c/pizza-shack/public/images/your-new-pizza.jpg`
3. **Ensure image uses `object-fit: cover` CSS property (already configured)**

#### 5. Update Price Ranges (if needed)

If your new pizza changes the price distribution, update the price ranges in:

- API: `main.py` price filter logic
- AI Agent: `get_menu.py` price range filters

#### 6. Restart Services & Test

```bash
# Stop services
./stop_services.sh

# Restart to reload menu data
./start_services.sh

# Test in browser:
# 1. View new pizza in menu
# 2. Add to cart and checkout
# 3. Ask AI assistant about the new pizza
# 4. Verify order placement works
```

#### 7. Update Documentation

Update the pizza catalog table in this README.md file with the new pizza details.

**Important Notes:**

- Always use consistent naming across all files
- Ensure price format matches existing patterns
- Test both frontend display and AI agent knowledge
- Verify image displays properly in 1:1 ratio
- Categories: `classic`, `premium`, `vegetarian`, `specialty`

## Security & Privacy

### Data Protection

- **Minimal Data Collection**: Only order details and contact info
- **Local Storage**: Profile IDs stored in user's browser only
- **Automatic Expiry**: Data automatically removed after 90 days
- **No Cross-Site Tracking**: Profiles are domain-specific

### Privacy Considerations

- Guest profiles are anonymous until linked to orders
- No personally identifiable information in profile IDs
- Users can clear browser data to remove all traces
- No server-side tracking without explicit consent

## 🎪 Demo Guide

### Live Demo Flow

**For Live Presentations:**

1. **Show Personalization** (2-3 minutes):
   - Navigate to http://localhost:5173/ and sign in
   - Point out "🌟 Your Personalized Picks" section with explanatory text
   - Highlight "✨ You Loved This Before!" badges on recommended pizzas
   - Explain the tooltip showing "Based on your last 3 orders and taste preferences"
   - Show how recommended pizzas appear first with "Order Again" buttons

2. **Demonstrate AI Assistant** (3-4 minutes):
   - Point out the prominent "🍕 Chat to Order" floating button
   - Show the AI prompt suggestion bar: "Need help? Ask our Pizza AI:"
   - Click suggestion chips like "Recommend a pizza" to open chat
   - Demonstrate natural conversation: "I want something spicy" or "Order my usual"
   - Show live order updates and delivery tracking in chat

3. **Interactive Experience** (1-2 minutes):
   - Use the "View Your Picks" button to scroll to recommendations
   - Add personalized items to cart using "Order Again" button
   - Show smooth animations and transitions

### Simulating User Profile

**To demo personalization features:**

1. **Create test user data** by completing 2-3 guest orders first
2. **Login with test account** to see personalized recommendations
3. **Use browser dev tools** to set localStorage for instant demo:

```javascript
// Set test profile in browser console
localStorage.setItem('pizza_profile_id', 'test_user_123');
// Reload page to see personalization features
```

### AI Assistant Test Phrases

**Demo-friendly conversation starters:**

- "What do you recommend?" → Shows AI analyzing preferences
- "I want something spicy" → Demonstrates smart filtering
- "Order my usual" → Shows how AI remembers past orders
- "Track my delivery" → Displays order status updates
- "What's in the Tandoori Chicken?" → Shows menu knowledge

## Testing

### Manual Testing Checklist

**Complete Personalization Flow (Guest → Login → Personalized Experience):**

1. ✅ **Guest Order Phase**:
   - Open application in incognito/private window
   - Add 2-3 different pizzas to cart as guest user
   - Complete guest checkout with valid information
   - Verify profile ID is stored in localStorage: `pizza_shack_profile_id`
   - Check browser console for CDP profile creation logs

2. ✅ **Login Transition Phase**:
   - On same browser, click "Login / Sign Up"
   - Complete Asgardeo authentication
   - Verify personalized hero section appears: "Your Personal Pizza Experience Awaits"
   - Check that previous guest profile ID is still in localStorage

3. ✅ **Personalized Experience Phase**:
   - Verify "⭐ Your Personalized Picks" section is visible (not "Our Menu")
   - Confirm previously ordered pizzas show "🧡 YOU LOVED THIS BEFORE!" badges
   - Test "Order Again" buttons vs regular "Add to Cart" buttons
   - Verify AI prompt bar appears: "Need help? Ask our Pizza AI:"

4. ✅ **AI Assistant Integration**:
   - Click suggestion chips and verify they pre-populate chat input
   - Test AI welcome message mentions "taste preferences"
   - Ask "What did I like last time?" and verify contextual response

**Guest User Flow:**

1. ✅ Add items to cart as guest user
2. ✅ Complete guest checkout with valid information
3. ✅ Verify profile ID is stored in localStorage
4. ✅ Refresh page and verify recommendations appear
5. ✅ Test order again and verify profile is updated

**Error Scenarios:**

1. ✅ Disable network and verify graceful degradation
2. ✅ Clear localStorage and verify app continues working
3. ✅ Set expired profile and verify cleanup on app start

**Configuration Testing:**

1. ✅ Set `VITE_CDP_ENABLED=false` and verify no CDP calls
2. ✅ Test with invalid CDP endpoint
3. ✅ Verify debug mode logging

### Automated Testing

```bash
# Run linting
npm run lint

# Build for production
npm run build
```

## Deployment

### Production Build

```bash
npm run build
```

### Environment Setup

**Production Environment Variables:**

```bash
VITE_CDP_ENABLED=true
VITE_CDP_BASE_URL=https://production-cdp-endpoint.com/v1.0
VITE_PROFILE_EXPIRY_DAYS=90
VITE_CDP_DEBUG=false
```

### Monitoring

**Key Metrics to Monitor:**

- CDP API response times
- Profile creation success rate
- Storage fallback usage
- Recommendation display rate

**Logging:**

- All CDP operations are logged with appropriate levels
- Debug mode provides detailed request/response logging
- Errors are logged as warnings (non-fatal)

## Troubleshooting

### Common Issues

**CDP Features Not Working:**

1. Check `VITE_CDP_ENABLED` is set to `true`
2. Verify CDP endpoint is accessible
3. Check browser console for error messages
4. Ensure localStorage is available

**Recommendations Not Showing:**

1. Verify guest order was completed successfully
2. Check profile ID exists in localStorage
3. Confirm CDP profile contains order data
4. Check network connectivity to CDP API

**Storage Issues:**

1. Clear browser data and test fresh
2. Check if localStorage is disabled
3. Verify fallback to sessionStorage works
4. Test in incognito mode

### Debug Mode

Enable detailed logging:

```bash
VITE_CDP_DEBUG=true
```

This will log all CDP operations, API calls, and storage operations to the browser console.

## Design System

This application uses a comprehensive modern design system. See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) for complete details including:

- **Color Palette**: Warm orange-amber scheme with semantic colors
- **Typography**: Inter font with 9-scale type system
- **Spacing**: 4px-based spacing scale for consistency
- **Components**: Modern cards, buttons, and layout patterns
- **Accessibility**: WCAG 2.1 AA compliant colors and interactions

### Key Design Features

- ✨ **Modern Visual Identity**: Clean, appetizing warm color palette
- 🎨 **Consistent Components**: Unified button styles, cards, and spacing
- 📱 **Responsive Layout**: Mobile-first design with fluid breakpoints
- ♿ **Accessible**: High contrast ratios and keyboard navigation
- 🎯 **Design Tokens**: CSS variables for maintainable theming

## Contributing

1. Follow existing code style and patterns
2. Use the design system tokens from `src/index.css`
3. Ensure all changes maintain graceful degradation
4. Update documentation for new features
5. Test thoroughly with various storage scenarios
6. Verify privacy and security implications
7. Maintain design consistency with the established system

## License

This project is part of the WSO2 IAM tutorial series.
