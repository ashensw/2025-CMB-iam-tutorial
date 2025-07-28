import React, { useState, useEffect, useRef } from 'react';
import { SignedIn, SignedOut, SignInButton, UserDropdown, useAsgardeo } from '@asgardeo/react';
import ChatBot from './components/ChatBot';
import OrderConfirmationModal from './components/OrderConfirmationModal';
import MyOrders from './components/MyOrders';
import cdpService from './services/cdpService';
import profileStorage from './utils/profileStorage';
import pizzaApiClient from './services/pizzaApiClient';
import tokenManager from './services/tokenManager';
import { debugTokenScopes, debugAsgardeoConfig } from './utils/tokenDebug';
import Preloader from './components/Preloader';
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
  const [pizzaMenu, setPizzaMenu] = useState([]);
  const [isMenuLoading, setIsMenuLoading] = useState(true);
  const [menuError, setMenuError] = useState(null);
  const menuFetchedRef = useRef(false);
  const profileLoadedRef = useRef(false);

  // Fetch additional user info and manage tokens when authenticated
  useEffect(() => {
    if (isSignedIn && !userInfo) {
      console.log('Basic user info:', user);
      setUserInfo(user);
      
      // Store token for API access and debug scopes
      getAccessToken().then(token => {
        if (token) {
          tokenManager.storeToken(token, 3600); // 1 hour expiry
          console.log('Token stored successfully');
          
          // Debug token scopes
          console.log('🔍 Debugging token scopes...');
          debugAsgardeoConfig();
          const scopeInfo = debugTokenScopes(token);
          
          if (!scopeInfo.hasOrderRead || !scopeInfo.hasOrderWrite) {
            console.warn('⚠️ Missing required Pizza API scopes!');
            console.warn('Expected: order:read, order:write');
            console.warn('Found pizza scopes:', scopeInfo.pizzaScopes);
            console.warn('Please check Asgardeo application configuration');
          }
        }
      }).catch(error => {
        console.error('Failed to get access token:', error);
      });
    }
  }, [isSignedIn, userInfo, user, getAccessToken]);

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
    // Only log when there's a meaningful change, not on every loading state change
    if (isLoading === false) {
      console.log('🔍 Auth status:', { 
        isSignedIn: isSignedIn,
        isLoading: isLoading,
        user: user ? 'User data available' : 'No user data'
      });
    }
    
    if (isSignedIn && isLoading === false && !profileLoadedRef.current) {
      console.log('✅ Loading user profile for authenticated user...');
      profileLoadedRef.current = true;
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
    } else if (isSignedIn === false && isLoading === false) {
      console.log('❌ Clearing recommendations for unauthenticated user...');
      // Clear recommendations for unauthenticated users
      setRecommendations([]);
      profileLoadedRef.current = false; // Reset flag for next login
    }
  }, [isSignedIn, isLoading]); // Use official hook values directly

  useEffect(() => {
    if (isMenuLoading) {
      document.body.classList.add('menu-loading');
    } else {
      document.body.classList.remove('menu-loading');
    }
  }, [isMenuLoading]);

  // Fetch menu from Pizza API once on mount
  useEffect(() => {
    const fetchMenu = async () => {
      // Prevent multiple fetches
      if (menuFetchedRef.current) {
        return;
      }
      
      try {
        setIsMenuLoading(true);
        setMenuError(null);
        console.log('🍕 Fetching menu from Pizza API...');
        
        // Try to get access token if user is signed in
        let accessToken = null;
        if (isSignedIn) {
          try {
            accessToken = await getAccessToken();
            console.log('🔑 Using access token for menu fetch');
          } catch (tokenError) {
            console.warn('⚠️ Could not get access token, proceeding without auth:', tokenError);
          }
        }
        
        const menuData = await pizzaApiClient.getMenu(accessToken);
        console.log('✅ Menu fetched successfully:', menuData);
        
        // Transform API data to match frontend format if needed
        const transformedMenu = menuData.map(item => ({
          id: item.id,
          name: item.name,
          price: `${item.price}`,
          img: item.image_url || item.image || `/images/${item.name.toLowerCase().replace(/ /g, '_')}.jpeg`,
          desc: item.description || item.desc || 'Delicious pizza made with fresh ingredients'
        }));
        
        setPizzaMenu(transformedMenu);
        menuFetchedRef.current = true; // Mark as fetched
      } catch (error) {
        console.error('❌ Failed to fetch menu from API:', error);
        console.log('📋 Using fallback menu data');
        setMenuError(error.message);
        setPizzaMenu(fallbackPizzaMenu);
        menuFetchedRef.current = true; // Mark as fetched even on error
      } finally {
        setIsMenuLoading(false);
      }
    };

    fetchMenu();
  }, []); // Only run once on mount


  // Fallback menu data (used if API fails)
  const fallbackPizzaMenu = [
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
      const price = parseFloat(item.price);
      return total + (price * item.quantity);
    }, 0);
  };

  const getCartItemCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const handleCheckout = async () => {
    if (isSignedIn) {
      try {
        const accessToken = tokenManager.getAccessToken();
        if (!accessToken) {
          alert('Authentication expired. Please sign in again.');
          signOut();
          return;
        }

        // Transform cart data for Pizza API
        const orderData = pizzaApiClient.transformCartToOrderData(cart, userInfo);
        
        // Place order via Pizza API
        const apiOrder = await pizzaApiClient.createOrder(orderData, accessToken);
        console.log('Order placed via Pizza API:', apiOrder);

        // Create/update CDP profile for authenticated user order
        const profileData = cdpService.formatOrderData(cart, userInfo);
        const createdProfile = await cdpService.createProfile(profileData);
        
        if (createdProfile && createdProfile.profile_id) {
          profileStorage.storeProfileId(createdProfile.profile_id);
          console.log('Authenticated user profile updated:', createdProfile.profile_id);
          // Reload recommendations after successful profile update for authenticated users
          loadUserProfile();
        }

        // Show order confirmation modal with API order details
        setOrderConfirmationData({
          total: apiOrder.total_amount || getCartTotal().toFixed(2),
          isAuthenticated: true,
          userInfo: userInfo,
          items: cart,
          orderId: apiOrder.order_id || ('ORD-' + Date.now()),
          apiOrderId: apiOrder.id
        });
        setShowOrderConfirmation(true);
        setCart([]);
        setIsCartOpen(false);
        
        // Auto-open chat after order placement
        setTimeout(() => {
          setProactiveChatMessage("Excellent choice! ✅ Your order is confirmed and our chefs are on it. I'll update you on its progress right here. Estimated delivery: 25-35 minutes.");
          setIsChatOpen(true);
        }, 3000);

      } catch (error) {
        console.error('Order placement failed:', error);
        alert(`Order failed: ${error.message}`);
        
        // Fallback to local order if API fails
        try {
          const profileData = cdpService.formatOrderData(cart, userInfo);
          const createdProfile = await cdpService.createProfile(profileData);
          
          if (createdProfile && createdProfile.profile_id) {
            profileStorage.storeProfileId(createdProfile.profile_id);
            loadUserProfile();
          }
        } catch (profileError) {
          console.warn('CDP profile update failed:', profileError);
        }
        
        setOrderConfirmationData({
          total: getCartTotal().toFixed(2),
          isAuthenticated: true,
          userInfo: userInfo,
          items: cart,
          orderId: 'ORD-LOCAL-' + Date.now(),
          apiOrderId: null,
          isOffline: true
        });
        setShowOrderConfirmation(true);
        setCart([]);
        setIsCartOpen(false);
      }
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
          <Preloader />
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
      
      {/* Main Content Area */}
      {/* ─── MENU VIEW ───────────────────────────── */}
      {currentView === 'menu' && (
        <div className="main-content-container">
          {isMenuLoading ? (
            // ─── Loading State: Only spinner and text ─────────────────────
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '400px',
                flexDirection: 'column',
                gap: '1rem',
              }}
            >
              <Preloader />
            </div>
          ) : (
            // ─── Loaded State: Banner, Header, Grid ──────────────────────
            <>
              {/* Promo Banner - Above everything */}
              <div className="promo-banner">
                <div className="promo-content">
                  <span className="promo-icon">🔥</span>
                  <span className="promo-text">
                    Today's Special: Fresh Sri Lankan Flavors • Free Delivery on Orders $25+
                  </span>
                </div>
              </div>

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

              {/* Menu Grid */}
              <div className="menu-grid">
                {(() => {
                  // 1) Clone & enrich the pizza list
                  const findPizzaByName = (name) =>
                    pizzaMenu.find(
                      (pz) =>
                        pz.name.toLowerCase().includes(name.toLowerCase()) ||
                        name.toLowerCase().includes(pz.name.toLowerCase())
                    );

                  const enhanced = pizzaMenu.map((pz) => ({
                    ...pz,
                    isRecommended: false,
                    recommendationTitle: null,
                    recommendationAction: null,
                  }));

                  // 2) Mark & sort recommendations if signed in
                  if (isSignedIn && recommendations.length) {
                    recommendations.forEach((rec) => {
                      const match = findPizzaByName(rec.subtitle);
                      if (match) {
                        const target = enhanced.find((e) => e.name === match.name);
                        if (target) {
                          target.isRecommended = true;
                          target.recommendationTitle = rec.title;
                          target.recommendationAction = rec.action || 'Add to Cart';
                        }
                      }
                    });
                    const recs = enhanced.filter((e) => e.isRecommended);
                    const others = enhanced.filter((e) => !e.isRecommended);
                    return [...recs, ...others];
                  }

                  // 3) Fallback: original order
                  return enhanced;
                })().map((pizza) => (
                  <div key={pizza.id} className="pizza-card">
                    <div className="pizza-image-container">
                      <img
                        src={pizza.img}
                        alt={pizza.name}
                        className="pizza-image"
                      />
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
                      <span className="pizza-price">${parseFloat(pizza.price).toFixed(2)}</span>
                      <button
                        className={`add-to-cart-btn ${
                          pizza.isRecommended ? 'order-again' : ''
                        }`}
                        onClick={() => addToCart(pizza)}
                      >
                        {pizza.isRecommended ? 'Order Again' : 'Add to Cart'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}





      


      {/* ─── ORDERS VIEW ─────────────────────────── */}
      {currentView === 'orders' && (
        <SignedIn>
          <div className="main-content-container orders-view">
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
                  <div className="cart-item-price">${parseFloat(item.price).toFixed(2)}</div>
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
              <span>${getCartTotal().toFixed(2)}</span>
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
          <span className="chat-title">🤖 Pizza Shack AI Assistant</span>
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
              <span>${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
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
              <span>${parseFloat(total).toFixed(2)}</span>
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