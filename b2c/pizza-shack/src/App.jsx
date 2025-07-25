import React, { useState, useEffect } from 'react';
import { SignedIn, SignedOut, SignInButton, UserDropdown, useAsgardeo } from '@asgardeo/react';
import ChatBot from './components/ChatBot';
import OrderConfirmationModal from './components/OrderConfirmationModal';
import MyOrders from './components/MyOrders';
import cdpService from './services/cdpService';
import profileStorage from './utils/profileStorage';
import './App.css';

function App() {
  // Use official Asgardeo React patterns
  const { user, signIn, signOut, isSignedIn, isLoading, getAccessToken } = useAsgardeo();
  
  // Create compatibility layer for backward compatibility with other components
  const state = {
    isAuthenticated: isSignedIn || false,
    isLoading: isLoading || false,
    username: user?.preferred_username || user?.username
  };
  
  const getBasicUserInfo = async () => {
    return user || null;
  };
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [currentView, setCurrentView] = useState('menu'); // 'menu' or 'orders'
  const [userInfo, setUserInfo] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [showOrderConfirmation, setShowOrderConfirmation] = useState(false);
  const [orderConfirmationData, setOrderConfirmationData] = useState(null);
  const [showGuestCheckout, setShowGuestCheckout] = useState(false);
  const [hasSeenTooltip, setHasSeenTooltip] = useState(false);
  const [proactiveChatMessage, setProactiveChatMessage] = useState(null);
  const [chatInputValue, setChatInputValue] = useState('');

  // Fetch additional user info when authenticated
  useEffect(() => {
    if (isSignedIn && !userInfo) {
      console.log('Basic user info:', user);
      setUserInfo(user);
    }
  }, [isSignedIn, userInfo, user]);

  // Function to load user profile and recommendations
  const loadUserProfile = async () => {
    try {
      profileStorage.clearExpiredProfiles();
      
      const storedProfileId = profileStorage.getStoredProfileId();
      if (storedProfileId) {
        try {
          const profileData = await cdpService.getProfile(storedProfileId);
          if (profileData) {
            const recs = cdpService.formatRecommendations(profileData);
            setRecommendations(recs);
            console.log('✅ Loaded recommendations:', recs);
          } else {
            profileStorage.removeProfileId();
            console.log('❌ Profile not found, cleared storage');
          }
        } catch (error) {
          console.warn('Could not load recommendations:', error);
          setRecommendations([]);
        }
      } else {
        console.log('ℹ️ No stored profile ID found');
        setRecommendations([]);
      }
    } catch (error) {
      console.warn('Error during profile initialization:', error);
      setRecommendations([]);
    }
  };

  // Load user profile and recommendations only for authenticated users
  useEffect(() => {
    console.log('🔍 Auth status:', { 
      isSignedIn: isSignedIn,
      isLoading: isLoading,
      user: user
    });
    
    if (isSignedIn && !isLoading) {
      console.log('✅ Loading user profile for authenticated user...');
      loadUserProfile();
      
      // Proactive welcome for logged-in users
      setTimeout(() => {
        if (user?.preferred_username || user?.username) {
          const username = user.preferred_username || user.username;
          setProactiveChatMessage(
            `Welcome back, ${username}! 👋 Your usual 'Spicy Jaffna Crab', or shall I recommend something new tonight?`
          );
          setIsChatOpen(true);
        }
      }, 2000); // Delay to allow page to fully load
    } else if (!isSignedIn && !isLoading) {
      console.log('❌ Clearing recommendations for unauthenticated user...');
      // Clear recommendations for unauthenticated users
      setRecommendations([]);
    }
  }, [isSignedIn, isLoading]); // Use official hook values directly


  const pizzaMenu = [
    { 
      id: 1,
      name: 'Tandoori Chicken', 
      price: '$14.99', 
      img: '/images/tandoori_chicken.jpeg', 
      desc: 'Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce' 
    },
    { 
      id: 2,
      name: 'Spicy Jaffna Crab', 
      price: '$16.50', 
      img: '/images/spicy_jaffna_crab.jpeg', 
      desc: 'Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!' 
    },
    { 
      id: 3,
      name: 'Curry Chicken & Cashew', 
      price: '$13.99', 
      img: '/images/curry_chicken_cashew.jpeg', 
      desc: 'Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!' 
    },
    { 
      id: 4,
      name: 'Spicy Paneer Veggie', 
      price: '$13.50', 
      img: '/images/spicy_paneer_veggie.jpeg', 
      desc: 'Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella' 
    },
    { 
      id: 5,
      name: 'Margherita Classic', 
      price: '$12.50', 
      img: '/images/margherita_classic.jpeg', 
      desc: 'Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves' 
    },
    { 
      id: 6,
      name: 'Four Cheese Fusion', 
      price: '$13.25', 
      img: '/images/four_cheese_fusion.jpeg', 
      desc: 'A cheese lover\'s dream with mozzarella, sharp cheddar, Parmesan, and creamy ricotta.' 
    },
    { 
      id: 7,
      name: 'Hot Butter Prawn', 
      price: '$15.50', 
      img: '/images/hot_butter_prawn.jpeg', 
      desc: 'Juicy prawns in signature hot butter sauce with mozzarella and spring onions.' 
    },
    { 
      id: 8,
      name: 'Masala Potato & Pea', 
      price: '$12.99', 
      img: '/images/masala_potato_pea.jpeg', 
      desc: 'Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella' 
    }
  ];

  const addToCart = (pizza) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === pizza.id);
      if (existingItem) {
        return prevCart.map(item => 
          item.id === pizza.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevCart, { ...pizza, quantity: 1 }];
    });
  };

  const updateCartQuantity = (pizzaId, newQuantity) => {
    if (newQuantity <= 0) {
      setCart(prevCart => prevCart.filter(item => item.id !== pizzaId));
    } else {
      setCart(prevCart => 
        prevCart.map(item => 
          item.id === pizzaId 
            ? { ...item, quantity: newQuantity }
            : item
        )
      );
    }
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const price = parseFloat(item.price.replace('$', '').replace(',', ''));
      return total + (price * item.quantity);
    }, 0);
  };

  const getCartItemCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const handleCheckout = async () => {
    if (isSignedIn) {
      try {
        // Create/update CDP profile for authenticated user order
        const profileData = cdpService.formatOrderData(cart, userInfo);
        const createdProfile = await cdpService.createProfile(profileData);
        
        if (createdProfile && createdProfile.profile_id) {
          profileStorage.storeProfileId(createdProfile.profile_id);
          console.log('Authenticated user profile updated:', createdProfile.profile_id);
          // Reload recommendations after successful profile update for authenticated users
          loadUserProfile();
        }
      } catch (error) {
        console.warn('CDP profile update failed for authenticated user (non-fatal):', error);
      }
      
      // Show order confirmation modal
      setOrderConfirmationData({
        total: getCartTotal().toFixed(2),
        isAuthenticated: true,
        userInfo: userInfo,
        items: cart,
        orderId: 'ORD-' + Date.now()
      });
      setShowOrderConfirmation(true);
      setCart([]);
      setIsCartOpen(false);
      
      // Auto-open chat after order placement (with delay for modal to show first)
      setTimeout(() => {
        setProactiveChatMessage("Excellent choice! ✅ Your order is confirmed and our chefs are on it. I'll update you on its progress right here. Estimated delivery: 25-35 minutes.");
        setIsChatOpen(true);
      }, 3000);
    } else {
      setShowGuestCheckout(true);
    }
  };

  const handleGuestCheckout = async (guestInfo) => {
    try {
      // Create CDP profile for guest order
      const profileData = cdpService.formatOrderData(cart, guestInfo);
      const createdProfile = await cdpService.createProfile(profileData);
      
      if (createdProfile && createdProfile.profile_id) {
        const stored = profileStorage.storeProfileId(createdProfile.profile_id);
        if (stored) {
          console.log('Guest profile created and stored successfully:', createdProfile.profile_id);
          // Note: Don't load recommendations for guest users - they will see them when they log in
        }
      }
      
      // Show order confirmation modal for guest users
      setOrderConfirmationData({
        total: getCartTotal().toFixed(2),
        isAuthenticated: false,
        userInfo: guestInfo,
        items: cart,
        orderId: 'ORD-' + Date.now()
      });
      setShowOrderConfirmation(true);
      setCart([]);
      setShowGuestCheckout(false);
      setIsCartOpen(false);
      
      // Guest users don't have access to chat - no auto-open needed
    } catch (error) {
      console.error('Unexpected error during guest checkout:', error);
      // Always continue with order completion
      setOrderConfirmationData({
        total: getCartTotal().toFixed(2),
        isAuthenticated: false,
        userInfo: guestInfo,
        items: cart,
        orderId: 'ORD-' + Date.now()
      });
      setShowOrderConfirmation(true);
      setCart([]);
      setShowGuestCheckout(false);
      setIsCartOpen(false);
      
      // Guest users don't have access to chat - no auto-open needed
    }
  };

  if (isLoading) {
    return (
      <div className="modern-app">
        <div style={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div className="loading-spinner"></div>
          <p>Loading Pizza Shack...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="modern-app">
      {/* Sticky Header - Always visible */}
      <header className="modern-header">
        <div className="header-content">
          <div className="header-logo" onClick={() => setCurrentView('menu')}>
            <img src="/images/logo.jpg" alt="Pizza Shack Logo" />
            <h1>Pizza Shack</h1>
          </div>
          
          <div className="header-actions">
            {/* My Orders Button - Only for authenticated users */}
            <SignedIn>
              <button 
                className="my-orders-button"
                onClick={() => setCurrentView('orders')}
              >
                📋 My Orders
              </button>
            </SignedIn>

            {/* Cart Button - Always visible */}
            <div className="cart-wrapper">
              <button 
                className="cart-button"
                onClick={() => setIsCartOpen(true)}
              >
                🛒 Cart
              </button>
              {getCartItemCount() > 0 && (
                <span className="cart-counter">
                  {getCartItemCount()}
                </span>
              )}
            </div>

            {/* User Actions */}
            <SignedIn>
              <div className="user-menu">
                <UserDropdown />
              </div>
            </SignedIn>
            
            <SignedOut>
              <SignInButton>
                {({ signIn }) => (
                  <button 
                    className="login-button"
                    onClick={signIn}
                  >
                    Login / Sign Up
                  </button>
                )}
              </SignInButton>
            </SignedOut>
          </div>
        </div>
      </header>


      {/* Promotional Banner - Container Width - Only show on menu view */}
      {currentView === 'menu' && (
        <div className="promo-banner">
          <div className="promo-content">
            <span className="promo-icon">🔥</span>
            <span className="promo-text">Today's Special: Fresh Sri Lankan Flavors • Free Delivery on Orders $25+</span>
          </div>
        </div>
      )}

      {currentView === 'menu' ? (
        <div className="main-content-container">
          {/* Menu Section Header */}
          <div className="menu-section-header">
            <SignedIn>
              {recommendations.length > 0 ? (
                <div className="personalized-section">
                  <h1 className="menu-page-title">🍕 Your Picks</h1>
                </div>
              ) : (
                <h1 className="menu-page-title">Our Menu</h1>
              )}
            </SignedIn>
            <SignedOut>
              <h1 className="menu-page-title">Our Menu</h1>
            </SignedOut>
          </div>
            <div className="menu-grid">
              {(() => {
                // Helper function to find pizza by recommendation name
                const findPizzaByName = (name) => {
                  return pizzaMenu.find(pizza => 
                    pizza.name.toLowerCase().includes(name.toLowerCase()) ||
                    name.toLowerCase().includes(pizza.name.toLowerCase())
                  );
                };

                // Create enhanced pizza array with recommendation data
                const enhancedPizzaMenu = pizzaMenu.map(pizza => ({
                  ...pizza,
                  isRecommended: false,
                  recommendationTitle: null,
                  recommendationAction: null
                }));

                // Mark recommended pizzas only for authenticated users
                if (isSignedIn && recommendations.length > 0) {
                  recommendations.forEach(rec => {
                    const matchingPizza = findPizzaByName(rec.subtitle);
                    if (matchingPizza) {
                      const enhancedPizza = enhancedPizzaMenu.find(p => p.name === matchingPizza.name);
                      if (enhancedPizza) {
                        enhancedPizza.isRecommended = true;
                        enhancedPizza.recommendationTitle = rec.title;
                        enhancedPizza.recommendationAction = rec.action || 'Add to Cart';
                      }
                    }
                  });

                  // Sort to show recommended pizzas first
                  const recommendedPizzas = enhancedPizzaMenu.filter(p => p.isRecommended);
                  const nonRecommendedPizzas = enhancedPizzaMenu.filter(p => !p.isRecommended);
                  return [...recommendedPizzas, ...nonRecommendedPizzas];
                }

                return enhancedPizzaMenu;
              })().map((pizza) => (
                <div key={pizza.id} className="pizza-card">
                  <div className="pizza-image-container">
                    <img 
                      src={pizza.img} 
                      alt={pizza.name}
                      className="pizza-image"
                    />
                    {/* Personalization Ribbon */}
                    {pizza.isRecommended && (
                      <div className="favorite-ribbon subtle">
                        💛 You liked this before!
                      </div>
                    )}
                  </div>
                  <div className="pizza-content">
                    <h3 className="pizza-title">{pizza.name}</h3>
                    <p className="pizza-description">{pizza.desc}</p>
                  </div>
                  <div className="pizza-footer">
                    <span className="pizza-price">{pizza.price}</span>
                    <button 
                      className={`add-to-cart-btn ${pizza.isRecommended ? 'order-again' : ''}`}
                      onClick={() => addToCart(pizza)}
                    >
                      {pizza.isRecommended ? 'Order Again' : 'Add to Cart'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
        </div>
      ) : (
        /* Orders View - Only for authenticated users */
        <SignedIn>
          <div className="main-content-container">
            {/* My Orders Section Header */}
            <div className="menu-section-header">
              <h1 className="menu-page-title">My Orders</h1>
            </div>
            <MyOrders onBackToMenu={() => setCurrentView('menu')} />
          </div>
        </SignedIn>
      )}

      {/* Cart Drawer */}
      <div className={`cart-drawer-overlay ${isCartOpen ? 'open' : ''}`} onClick={() => setIsCartOpen(false)} />
      <div className={`cart-drawer ${isCartOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h3 className="cart-title">Your Order</h3>
          <button className="close-cart" onClick={() => setIsCartOpen(false)}>
            ×
          </button>
        </div>
        
        <div className="cart-items">
          {cart.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '2rem', 
              color: 'var(--text-secondary)' 
            }}>
              Your cart is empty
            </div>
          ) : (
            cart.map((item) => (
              <div key={item.id} className="cart-item">
                <img 
                  src={item.img} 
                  alt={item.name}
                  className="cart-item-image"
                />
                <div className="cart-item-details">
                  <div className="cart-item-name">{item.name}</div>
                  <div className="cart-item-price">{item.price}</div>
                </div>
                <div className="quantity-controls">
                  <button 
                    className="qty-btn"
                    onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                  >
                    −
                  </button>
                  <span className="qty-display">{item.quantity}</span>
                  <button 
                    className="qty-btn"
                    onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                  >
                    +
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
        
        {cart.length > 0 && (
          <div className="cart-footer">
            <div className="cart-total">
              <span>Total:</span>
              <span>${getCartTotal().toLocaleString()}</span>
            </div>
            <button className="checkout-btn" onClick={handleCheckout}>
              Proceed to Checkout
            </button>
          </div>
        )}
      </div>

      {/* Enhanced AI Assistant FAB - Only for authenticated users */}
      <SignedIn>
        <div className="ai-fab-container">
          <button 
            className="chat-fab"
            onClick={() => {
              setIsChatOpen(true);
              setHasSeenTooltip(true);
            }}
            title="AI Assistant"
          >
            💬
          </button>
          <div className="ai-fab-tooltip">AI Assistant</div>
          {/* First-visit tooltip */}
          {!hasSeenTooltip && (
            <div className="ai-tooltip">
              👋 Need help? Try: "Recommend a pizza" or "Order again"
            </div>
          )}
        </div>
      </SignedIn>

      {/* Chat Window - Corner Anchored */}
      <div className={`chat-window ${isChatOpen ? 'open' : ''}`}>
        <div className="chat-header">
          <span className="chat-title">🤖 Pizza AI Assistant</span>
          <button className="close-chat" onClick={() => setIsChatOpen(false)}>
            ×
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <ChatBot 
            isEmbedded={true} 
            initialInput={chatInputValue}
            onInputCleared={() => setChatInputValue('')}
          />
        </div>
      </div>

      {/* Guest Checkout Modal */}
      {showGuestCheckout && (
        <GuestCheckoutModal 
          cart={cart}
          total={getCartTotal().toFixed(2)}
          onCheckout={handleGuestCheckout}
          onClose={() => setShowGuestCheckout(false)}
        />
      )}

      {/* Order Confirmation Modal */}
      {showOrderConfirmation && orderConfirmationData && (
        <OrderConfirmationModal
          isOpen={showOrderConfirmation}
          orderDetails={orderConfirmationData}
          userInfo={orderConfirmationData.userInfo}
          onCreateAccount={!orderConfirmationData.isAuthenticated ? () => signIn() : undefined}
          onClose={() => {
            setShowOrderConfirmation(false);
            setOrderConfirmationData(null);
          }}
        />
      )}
    </div>
  );
}

// Guest Checkout Modal Component
const GuestCheckoutModal = ({ cart, total, onCheckout, onClose }) => {
  const [guestInfo, setGuestInfo] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    zipCode: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCheckout(guestInfo);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 4000
    }}>
      <div style={{
        background: 'white',
        borderRadius: '1rem',
        padding: '2rem',
        width: '500px',
        maxWidth: '90vw',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
      }}>
        <h2 style={{ 
          color: 'var(--text-primary)', 
          textAlign: 'center', 
          marginBottom: '1.5rem', 
          fontSize: '1.5rem',
          fontWeight: '700'
        }}>
          Guest Checkout
        </h2>
        
        <div style={{ 
          marginBottom: '1.5rem', 
          padding: '1rem', 
          background: 'var(--bg-primary)', 
          borderRadius: '0.5rem' 
        }}>
          <h4 style={{ 
            margin: '0 0 0.5rem 0', 
            color: 'var(--text-primary)',
            fontWeight: '600'
          }}>
            Order Summary:
          </h4>
          {cart.map((item, index) => (
            <div key={index} style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              marginBottom: '0.25rem',
              fontSize: '0.875rem'
            }}>
              <span>{item.name} x{item.quantity}</span>
              <span>${(parseFloat(item.price.replace('$', '').replace(',', '')) * item.quantity).toLocaleString()}</span>
            </div>
          ))}
          <div style={{ 
            borderTop: '1px solid var(--border-medium)', 
            paddingTop: '0.5rem', 
            marginTop: '0.5rem', 
            fontWeight: '700' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Total:</span>
              <span>${parseFloat(total).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <input
              type="text"
              placeholder="Full Name *"
              value={guestInfo.name}
              onChange={(e) => setGuestInfo({ ...guestInfo, name: e.target.value })}
              required
              style={{
                padding: '0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-medium)',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif'
              }}
            />
            <input
              type="email"
              placeholder="Email *"
              value={guestInfo.email}
              onChange={(e) => setGuestInfo({ ...guestInfo, email: e.target.value })}
              required
              style={{
                padding: '0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-medium)',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif'
              }}
            />
          </div>
          
          <input
            type="tel"
            placeholder="Phone Number *"
            value={guestInfo.phone}
            onChange={(e) => setGuestInfo({ ...guestInfo, phone: e.target.value })}
            required
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              border: '1px solid var(--border-medium)',
              fontSize: '0.875rem',
              fontFamily: 'Inter, sans-serif'
            }}
          />
          
          <input
            type="text"
            placeholder="Delivery Address *"
            value={guestInfo.address}
            onChange={(e) => setGuestInfo({ ...guestInfo, address: e.target.value })}
            required
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              border: '1px solid var(--border-medium)',
              fontSize: '0.875rem',
              fontFamily: 'Inter, sans-serif'
            }}
          />
          
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
            <input
              type="text"
              placeholder="City *"
              value={guestInfo.city}
              onChange={(e) => setGuestInfo({ ...guestInfo, city: e.target.value })}
              required
              style={{
                padding: '0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-medium)',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif'
              }}
            />
            <input
              type="text"
              placeholder="Zip Code *"
              value={guestInfo.zipCode}
              onChange={(e) => setGuestInfo({ ...guestInfo, zipCode: e.target.value })}
              required
              style={{
                padding: '0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-medium)',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif'
              }}
            />
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                flex: 1,
                background: 'var(--text-secondary)',
                color: 'white',
                border: 'none',
                padding: '0.75rem',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                cursor: 'pointer',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={{
                flex: 2,
                background: 'var(--primary-orange)',
                color: 'white',
                border: 'none',
                padding: '0.75rem',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              Place Order - ${parseFloat(total).toLocaleString()}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default App;