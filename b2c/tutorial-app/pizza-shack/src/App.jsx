import { SignedIn, SignedOut, SignInButton, SignOutButton, UserDropdown } from '@asgardeo/react'
import './App.css'

function App() {
  return (
    <>
      <SignedIn>
        <div className="app-container">
          <nav className="top-nav">
            <img src="/images/logo.jpg" alt="Pizza Shack Logo" className="logo" />
            <h1>Pizza Shack</h1>
            <div className="nav-buttons">
              <UserDropdown />
            </div>
          </nav>

          <header>
            <p>🍕 Delicious Pizza Delivered Fresh to Your Door! 🚚</p>
          </header>

          <main>
            {/* Pizza Menu Section */}
            <section className="menu">
              <h2>Our Menu</h2>
              <ul>
                <li>
                  <img src="/images/margherita.jpg" alt="Margherita Pizza" />
                  <div className="pizza-info">
                    <h3>Margherita Classic</h3>
                    <span className="pizza-price">$10.99</span>
                  </div>
                </li>
                <li>
                  <img src="/images/4-cheese.jpg" alt="Four Cheese Pizza" />
                  <div className="pizza-info">
                    <h3>Four Cheese Deluxe</h3>
                    <span className="pizza-price">$12.99</span>
                  </div>
                </li>
                <li>
                  <img src="/images/pizza-marinara.jpg" alt="Pizza Marinara" />
                  <div className="pizza-info">
                    <h3>Marinara Special</h3>
                    <span className="pizza-price">$11.49</span>
                  </div>
                </li>
                <li>
                  <img src="/images/pepperoni.jpg" alt="Pepperoni Pizza" />
                  <div className="pizza-info">
                    <h3>Pepperoni Supreme</h3>
                    <span className="pizza-price">$13.99</span>
                  </div>
                </li>
                <li>
                  <img src="/images/veggie.jpg" alt="Veggie Pizza" />
                  <div className="pizza-info">
                    <h3>Veggie Garden</h3>
                    <span className="pizza-price">$11.99</span>
                  </div>
                </li>
              </ul>
            </section>

            {/* Order Form Section */}
            <section className="order">
              <h2>Place Your Order</h2>
              <form onSubmit={(e) => { e.preventDefault(); alert('Order placed successfully! 🍕'); }}>
                <div className="form-group">
                  <label htmlFor="pizzaSelect">Choose Your Pizza:</label>
                  <select id="pizzaSelect" name="pizza" required>
                    <option value="">-- Select a pizza --</option>
                    <option value="margherita-classic">Margherita Classic ($10.99)</option>
                    <option value="four-cheese-deluxe">Four Cheese Deluxe ($12.99)</option>
                    <option value="marinara-special">Marinara Special ($11.49)</option>
                    <option value="pepperoni-supreme">Pepperoni Supreme ($13.99)</option>
                    <option value="veggie-garden">Veggie Garden ($11.99)</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="quantity">Quantity:</label>
                  <div className="quantity-controls">
                    <button type="button" className="qty-btn" onClick={(e) => {
                      const input = e.target.nextElementSibling;
                      if (input.value > 1) input.value = parseInt(input.value) - 1;
                    }}>-</button>
                    <input type="number" id="quantity" name="quantity" min="1" max="10" defaultValue="1" />
                    <button type="button" className="qty-btn" onClick={(e) => {
                      const input = e.target.previousElementSibling;
                      if (input.value < 10) input.value = parseInt(input.value) + 1;
                    }}>+</button>
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="specialInstructions">Special Instructions:</label>
                  <textarea 
                    id="specialInstructions" 
                    name="instructions" 
                    placeholder="Any special requests?"
                    rows="2"
                  ></textarea>
                </div>
                
                <button type="submit" className="order-btn">
                  Place Order Now
                </button>
              </form>
            </section>
          </main>

          <footer>
            <p>&copy; {new Date().getFullYear()} Pizza Shack. All rights reserved.</p>
          </footer>
        </div>
      </SignedIn>
      <SignedOut>
        <div className="login-background">
          <div className="login-box">
            <img src="/images/logo.jpg" alt="Pizza Shack Logo" className="login-logo" />
            <h1>Pizza Shack</h1>
            <p>Your favorite pizza delivery app!</p>
            <p>Please login</p>
            <SignInButton>
              {({ signIn }) => (
                <button onClick={signIn}>
                  Login
                </button>
              )}
            </SignInButton>
          </div>
        </div>
      </SignedOut>
    </>
  )
}

export default App;
