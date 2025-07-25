import React, { useState, useEffect } from 'react';
import { useAsgardeo } from '@asgardeo/react';

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
      const accessToken = await getAccessToken();
      
      console.log('Fetching orders with token:', accessToken ? 'present' : 'missing');
      
      const response = await fetch('http://localhost:8000/api/orders', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        console.error('API Error:', response.status, errorData);
        throw new Error(`API Error: ${errorData.error || response.statusText}`);
      }

      const ordersData = await response.json();
      console.log('Orders fetched successfully:', ordersData.length, 'orders');
      setOrders(ordersData);
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError(`Failed to load orders: ${err.message}`);
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

  if (loading) {
    return (
      <div className="orders-main-card">
        <div className="orders-content-area">
          <div className="back-to-menu-section">
            <button className="back-to-menu-btn" onClick={onBackToMenu}>
              ← Back to Menu
            </button>
          </div>
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p className="loading-text">Loading your orders...</p>
          </div>
        </div>
      </div>
    );
  }

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
        <div className="back-to-menu-section">
          <button className="back-to-menu-btn" onClick={() => window.history.back()}>
            ← Back to Menu
          </button>
        </div>
        
        <div className="orders-header">
          {/* Filter buttons */}
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

        {filteredOrders.length === 0 ? (
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
                  <div key={order.id} className="order-card">
                    {/* Order header */}
                    <div className="order-header">
                      <div className="order-info">
                        <h3 className="order-title">
                          Order #{order.order_id}
                        </h3>
                        <p className="order-date">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                      
                      {/* Creator badge */}
                      <div className={`creator-badge ${creator.type}`}>
                        <span>{creator.icon}</span>
                        <span>{creator.label}</span>
                      </div>
                    </div>

                    {/* Order items */}
                    <div className="order-items-section">
                      <h4 className="items-heading">
                        Order Items:
                      </h4>
                      <div className="items-list">
                        {order.items.map((item, index) => (
                          <div key={index} className="item-card">
                            <div className="item-details">
                              <div className="item-name">
                                {item.name}
                              </div>
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

                    {/* Order summary */}
                    <div className="order-summary">
                      <div className="status-section">
                        <div className={`status-badge ${order.status}`}>
                          {order.status.toUpperCase()}
                        </div>
                        {creator.type === 'agent' && order.agent_id && (
                          <div className="agent-info">
                            Agent ID: {order.agent_id.substring(0, 8)}...
                          </div>
                        )}
                      </div>
                      
                      <div className="order-total">
                        Total: ${order.total_amount.toFixed(2)}
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyOrders;