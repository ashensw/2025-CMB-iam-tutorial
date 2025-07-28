import React, { useState, useEffect } from 'react';
import { useAsgardeo } from '@asgardeo/react';
import pizzaApiClient from '../services/pizzaApiClient';
import tokenManager from '../services/tokenManager';

const MyOrders = ({ onBackToMenu }) => {
  const authContext = useAsgardeo();
  const getAccessToken = () => authContext?.getAccessToken();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, user, agent

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError(null);

      const accessToken = tokenManager.getAccessToken();
      if (!accessToken) {
        throw new Error('Authentication expired. Please sign in again.');
      }
      
      console.log('Fetching orders from Pizza API...');
      
      // Use Pizza API client to fetch orders
      const ordersData = await pizzaApiClient.getUserOrders(accessToken);
      console.log('Orders fetched successfully:', ordersData.length, 'orders');
      setOrders(ordersData);
      
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError(`Failed to load orders: ${err.message}`);
      
      // Fallback to local endpoint if Pizza API fails
      try {
        console.log('Attempting fallback to local API...');
        const accessToken = await getAccessToken();
        
        const headers = {
          'Authorization': `Bearer ${accessToken}`,
          'X-JWT-Assertion': accessToken,  // Add JWT assertion header for Pizza API
          'Content-Type': 'application/json'
        };

        // Note: Choreo API key is only needed for menu calls, not for authenticated order calls

        const response = await fetch('http://localhost:8000/api/orders', {
          headers
        });

        if (response.ok) {
          const localOrders = await response.json();
          console.log('Fallback orders loaded:', localOrders.length);
          setOrders(localOrders);
          setError(null); // Clear error if fallback works
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        // Keep original error message
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter(order => {
    if (filter === 'all') return true;
    if (filter === 'user') return !order.agent_id || order.token_type !== 'obo';
    if (filter === 'agent') return order.agent_id && order.token_type === 'obo';
    return true;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCreatorInfo = (order) => {
    if (order.agent_id && order.token_type === 'obo') {
      return {
        type: 'agent',
        label: 'via Pizza AI Agent',
        icon: '🤖',
        color: '#2A4B3D'
      };
    } else {
      return {
        type: 'user',
        label: 'Created by You',
        icon: '👤',
        color: '#D96F32'
      };
    }
  };

  const SkeletonLoader = () => (
    <div className="orders-grid">
      {[1, 2, 3].map((index) => (
        <div key={`skeleton-order-${index}`} className="order-card skeleton-card">
          <div className="order-header">
            <div className="order-info">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-date"></div>
            </div>
            <div className="skeleton-tag"></div>
          </div>
          <div className="order-items-section">
            <div className="skeleton-line skeleton-heading"></div>
            <div className="items-list">
              {[1, 2].map((itemIndex) => (
                <div key={`skeleton-item-${index}-${itemIndex}`} className="item-card">
                  <div className="item-details">
                    <div className="skeleton-line skeleton-item-name"></div>
                    <div className="skeleton-line skeleton-item-meta"></div>
                  </div>
                  <div className="skeleton-line skeleton-price"></div>
                </div>
              ))}
            </div>
          </div>
          <div className="order-summary">
            <div className="skeleton-tag skeleton-status"></div>
            <div className="skeleton-line skeleton-total"></div>
          </div>
        </div>
      ))}
    </div>
  );

  if (error) {
    return (
      <div className="orders-main-card">
        <div className="orders-content-area">
          <div className="back-to-menu-section">
            <button className="back-to-menu-btn" onClick={onBackToMenu}>
              ← Back to Menu
            </button>
          </div>
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h3 className="error-heading">Something went wrong</h3>
            <p className="error-subtext">We couldn't load your order history. Please check your internet connection and try again.</p>
            <button className="try-again-btn" onClick={fetchOrders}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="orders-main-card">
      <div className="orders-content-area">
        {/* Static header - always present */}
        <div className="orders-static-header">
          <div className="back-to-menu-section">
            <button className="back-to-menu-btn" onClick={onBackToMenu}>
              ← Back to Menu
            </button>
          </div>
          
          <h1 className="orders-page-title">My Orders</h1>
          
          <div className="orders-header">
            <div className="filter-buttons">
              {[
                { key: 'all', label: 'All Orders' },
                { key: 'user', label: 'My Orders' },
                { key: 'agent', label: 'AI Agent Orders' }
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key)}
                  className={`filter-btn ${filter === key ? 'active' : ''}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Dynamic content area */}
        <div className="orders-dynamic-content">
          {loading ? (
            <SkeletonLoader />
          ) : filteredOrders.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🍕</div>
              <h3 className="empty-heading">
                {filter === 'all' ? 'No orders yet' : 
                 filter === 'user' ? 'No direct orders yet' : 
                 'No AI agent orders yet'}
              </h3>
              <p className="empty-subtext">
                {filter === 'all' ? 'Place your first order to see it here!' :
                 filter === 'user' ? 'Orders you place directly will appear here.' :
                 'Orders placed by the AI agent will appear here.'}
              </p>
            </div>
          ) : (
            <div className="orders-grid">
              {filteredOrders
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .map((order) => {
                  const creator = getCreatorInfo(order);
                  
                  return (
                    <div key={`order-${order.id}-${order.order_id}`} className="order-card">
                      {/* Order header with new structure */}
                      <div className="order-header">
                        <div className="order-info">
                          <div className="order-id-date">
                            <h3 className="order-id">Order #{order.order_id}</h3>
                            <p className="order-date">{formatDate(order.created_at)}</p>
                          </div>
                          <div className="order-status-tags">
                            <div className={`status-tag ${order.status}`}>
                              {order.status.toUpperCase()}
                            </div>
                          </div>
                        </div>
                        
                        <div className="order-summary-info">
                          <div className="order-total-header">
                            ${order.total_amount.toFixed(2)}
                          </div>
                          <div className={`source-tag ${creator.type}`}>
                            {creator.label}
                          </div>
                        </div>
                      </div>

                      {/* Order items with better alignment */}
                      <div className="order-items-section">
                        <div className="items-list">
                          {order.items.map((item, index) => (
                            <div key={`order-${order.id}-item-${index}-${item.menu_item_id || item.id || Math.random()}`} className="item-row">
                              <div className="item-details">
                                <div className="item-name">{item.name}</div>
                                <div className="item-meta">
                                  Size: {item.size} • Qty: {item.quantity}
                                </div>
                                {item.special_instructions && (
                                  <div className="item-note">
                                    Note: {item.special_instructions}
                                  </div>
                                )}
                              </div>
                              <div className="item-price">
                                ${item.total_price.toFixed(2)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MyOrders;