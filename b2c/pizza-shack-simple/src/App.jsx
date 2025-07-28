import React from 'react';
import { SignedIn, SignedOut, SignInButton, UserDropdown, useAsgardeo } from '@asgardeo/react';
import './App.css';

function App() {
  const { isLoading } = useAsgardeo();

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
      <header className="modern-header">
        <div className="header-content">
          <div className="header-logo">
            <img src="/images/logo.jpg" alt="Pizza Shack Logo" />
            <h1>Pizza Shack</h1>
          </div>
          
          <div className="header-actions">
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
      
      <div className="main-content-container">
        <div className="menu-section-header">
          <h1 className="menu-page-title">Our Menu</h1>
        </div>

        <div className="menu-grid">
          {pizzaMenu.map((pizza) => (
            <div key={pizza.id} className="pizza-card">
              <div className="pizza-image-container">
                <img
                  src={pizza.img}
                  alt={pizza.name}
                  className="pizza-image"
                />
              </div>
              <div className="pizza-content">
                <h3 className="pizza-title">{pizza.name}</h3>
                <p className="pizza-description">{pizza.desc}</p>
              </div>
              <div className="pizza-footer">
                <span className="pizza-price">{pizza.price}</span>
                <button
                  className='add-to-cart-btn'
                >
                  Order Now
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
