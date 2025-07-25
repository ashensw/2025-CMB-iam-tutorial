import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAsgardeo } from '@asgardeo/react';
import './ChatBot.css';

const ChatBot = ({ isEmbedded = false, initialInput = '', onInputCleared = () => {} }) => {
  const authContext = useAsgardeo();
  const state = {
    isAuthenticated: authContext?.isAuthenticated || false,
    username: authContext?.user?.preferred_username || authContext?.user?.username
  };
  const [isOpen, setIsOpen] = useState(isEmbedded ? true : false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substring(7)}`);
  const [wsConnection, setWsConnection] = useState(null);
  const [authPopup, setAuthPopup] = useState(null);
  const [pendingOrder, setPendingOrder] = useState(null);
  const [showOrderConfirmation, setShowOrderConfirmation] = useState(false);
  const messagesEndRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Enhanced WebSocket connection with Hotel Agent patterns
  const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = `ws://localhost:8001/chat?session_id=${sessionId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected successfully');
        setIsConnected(true);
        setIsLoading(false);
        
        // Clear any reconnection timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
        
        // Add connection and welcome messages in correct order (only if not already present)
        setMessages(prev => {
          const hasConnectionMessage = prev.some(msg => 
            msg.content.includes('Connected to Pizza Shack AI agent!')
          );
          
          if (!hasConnectionMessage) {
            const connectionMessage = {
              id: Date.now().toString(),
              content: '🔗 Connected to Pizza Shack AI agent!',
              isUser: false,
              timestamp: new Date(),
              sender: 'assistant'
            };
            
            const welcomeMessage = {
              id: Date.now() + 1,
              content: `Hello ${state.username || 'there'}! 🍕 Welcome to Pizza Shack! I'm your personal Pizza AI with access to your taste preferences. I can help you reorder favorites, discover new pizzas based on what you've enjoyed before, or explore our full menu. What can I help you with today?`,
              isUser: false,
              timestamp: new Date(),
              sender: 'assistant'
            };
            
            return [connectionMessage, welcomeMessage];
          }
          
          return prev;
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          if (data.type === 'auth_request') {
            // Handle authentication request - show confirmation first
            handleOrderConfirmation(data);
          } else if (data.type === 'message') {
            // Handle regular chat message
            const botMessage = {
              id: Date.now().toString(),
              content: formatBotMessage(data.content),
              isUser: false,
              timestamp: new Date(),
              sender: data.sender || 'assistant'
            };
            setMessages(prev => [...prev, botMessage]);
          } else if (data.type === 'error') {
            // Handle error messages
            const errorMessage = {
              id: Date.now().toString(),
              content: `❌ Error: ${data.message || 'Something went wrong'}`,
              isUser: false,
              timestamp: new Date(),
              sender: 'assistant'
            };
            setMessages(prev => [...prev, errorMessage]);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setWsConnection(null);
        
        // Attempt to reconnect after a delay (unless intentionally closed)
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket();
          }, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      setWsConnection(ws);
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setIsConnected(false);
    }
  }, [sessionId]);

  // Handle order confirmation before authentication
  const handleOrderConfirmation = (authData) => {
    console.log('Handling order confirmation:', authData);
    
    // Store the auth data for later use
    setPendingOrder(authData);
    setShowOrderConfirmation(true);
    
    // Add order confirmation message
    const confirmMessage = {
      id: Date.now().toString(),
      content: '🍕 Ready to place your order! Please confirm to proceed with authentication and complete your order.',
      isUser: false,
      timestamp: new Date(),
      sender: 'assistant'
    };
    setMessages(prev => [...prev, confirmMessage]);
  };

  // Handle authentication request with popup (Hotel Agent pattern)
  const handleAuthRequest = (authData) => {
    console.log('Handling auth request:', authData);
    
    try {
      // Open authentication popup
      const popup = window.open(
        authData.auth_url,
        'pizza-shack-auth',
        'width=600,height=700,scrollbars=yes,resizable=yes,centerscreen=yes'
      );
      
      setAuthPopup(popup);
      
      // Add authentication in progress message
      const authMessage = {
        id: Date.now().toString(),
        content: '🔐 Opening authentication window... Please log in to place your order.',
        isUser: false,
        timestamp: new Date(),
        sender: 'assistant'
      };
      setMessages(prev => [...prev, authMessage]);
      
      // Monitor popup status
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          setAuthPopup(null);
        }
      }, 1000);
      
    } catch (error) {
      console.error('Failed to open authentication popup:', error);
      const errorMessage = {
        id: Date.now().toString(),
        content: '❌ Failed to open authentication window. Please try again.',
        isUser: false,
        timestamp: new Date(),
        sender: 'assistant'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Confirm order and proceed with authentication
  const confirmOrder = () => {
    if (pendingOrder) {
      setShowOrderConfirmation(false);
      handleAuthRequest(pendingOrder);
      setPendingOrder(null);
    }
  };

  // Cancel order
  const cancelOrder = () => {
    setShowOrderConfirmation(false);
    setPendingOrder(null);
    
    const cancelMessage = {
      id: Date.now().toString(),
      content: '❌ Order cancelled. Feel free to ask about our menu or try ordering again!',
      isUser: false,
      timestamp: new Date(),
      sender: 'assistant'
    };
    setMessages(prev => [...prev, cancelMessage]);
  };

  // Listen for authentication completion messages
  useEffect(() => {
    const handleMessage = (event) => {
      // Accept messages from our WebSocket service
      if (event.origin !== 'http://localhost:8001') return;
      
      if (event.data.type === 'auth_callback' && event.data.success) {
        console.log('Authentication successful:', event.data);
        
        // Close popup if open
        if (authPopup) {
          authPopup.close();
          setAuthPopup(null);
        }
        
        // Don't add success message - order confirmation will indicate success
        // The backend will send the order completion message automatically
        
      } else if (event.data.type === 'auth_callback' && !event.data.success) {
        console.log('Authentication failed:', event.data);
        
        // Close popup if open
        if (authPopup) {
          authPopup.close();
          setAuthPopup(null);
        }
        
        // Add error message
        const errorMessage = {
          id: Date.now().toString(),
          content: '❌ Authentication failed. Please try again.',
          isUser: false,
          timestamp: new Date(),
          sender: 'assistant'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [authPopup]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (isOpen) {
      connectWebSocket();
    }
    
    return () => {
      if (wsConnection) {
        wsConnection.close(1000, 'Component unmounting');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [isOpen, connectWebSocket]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle initial input from parent component
  useEffect(() => {
    if (initialInput && initialInput !== input) {
      setInput(initialInput);
      // Clear the initial input in parent after setting
      setTimeout(() => {
        onInputCleared();
      }, 100);
    }
  }, [initialInput, input, onInputCleared]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !isConnected) return;

    const userMessage = {
      id: Date.now().toString(),
      content: input,
      isUser: true,
      timestamp: new Date(),
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = input;
    setInput('');
    setIsLoading(true);

    try {
      if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        // Send message via WebSocket
        wsConnection.send(messageToSend);
      } else {
        throw new Error('WebSocket not connected');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: "❌ Connection error. Trying to reconnect... Please wait a moment and try again.",
        isUser: false,
        timestamp: new Date(),
        sender: 'assistant'
      };
      setMessages(prev => [...prev, errorMessage]);
      
      // Attempt to reconnect
      connectWebSocket();
    } finally {
      setIsLoading(false);
    }
  };

  const formatBotMessage = (content) => {
    // Check if content is a JSON string and try to parse it
    if (typeof content === 'string' && (content.startsWith('{') || content.startsWith('['))) {
      try {
        const parsed = JSON.parse(content);
        
        // Handle different response structures
        if (parsed.choices && parsed.choices[0] && parsed.choices[0].message) {
          // OpenAI-style response
          return parsed.choices[0].message.content || content;
        } else if (parsed.response) {
          // Generic response wrapper
          return parsed.response;
        } else if (parsed.content) {
          // Direct content field
          return parsed.content;
        } else if (parsed.message) {
          // Message field
          return parsed.message;
        } else if (typeof parsed === 'string') {
          // Parsed to a string
          return parsed;
        } else {
          // Return the original content if we can't extract meaningful text
          return content;
        }
      } catch (e) {
        // If parsing fails, return original content
        return content;
      }
    }
    
    // Return content as-is if it's not a JSON string
    return content;
  };

  const formatMessage = (content) => {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return { text: 'Connected', color: '#D96F32', icon: '🟢' };
    } else if (isLoading) {
      return { text: 'Connecting...', color: '#ffc107', icon: '🟡' };
    } else {
      return { text: 'Disconnected', color: '#dc3545', icon: '🔴' };
    }
  };

  if (!isOpen && !isEmbedded) {
    return (
      <div className="chatbot-trigger" onClick={() => setIsOpen(true)}>
        💬
        <span className="chatbot-badge">🍕</span>
      </div>
    );
  }

  const containerStyle = isEmbedded ? {
    position: 'relative',
    height: '100%',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    border: 'none',
    borderRadius: 0,
    boxShadow: 'none',
    background: 'transparent',
    overflow: 'hidden',
    bottom: 'auto',
    right: 'auto',
    left: 'auto',
    top: 'auto'
  } : {};

  const status = getConnectionStatus();

  return (
    <div className="chatbot-container" style={containerStyle}>
      {!isEmbedded && (
        <div className="chatbot-header">
          <div className="chatbot-header-content">
            🤖
            <span>Enhanced Pizza Assistant</span>
            <span style={{ 
              fontSize: '0.7rem', 
              color: status.color,
              marginLeft: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.2rem'
            }}>
              {status.icon} {status.text}
            </span>
          </div>
          <button className="chatbot-close" onClick={() => setIsOpen(false)}>
            ❌
          </button>
        </div>
      )}

      {/* Connection Status for Embedded Mode */}
      {isEmbedded && (
        <div style={{
          padding: '0.5rem 1rem',
          background: '#f8f9fa',
          borderBottom: '1px solid #e9ecef',
          fontSize: '0.8rem',
          color: status.color,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          justifyContent: 'center'
        }}>
          {status.icon} {status.text}
        </div>
      )}

      <div className="chatbot-messages" style={isEmbedded ? { 
        flex: 1, 
        padding: '1rem',
        overflowY: 'auto',
        minHeight: 0,
        maxHeight: 'none',
        background: 'white'
      } : {}}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}
          >
            <div className="message-avatar">
              {message.isUser ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div
                className="message-text"
                dangerouslySetInnerHTML={{
                  __html: formatMessage(message.content)
                }}
              />
              <div className="message-time">
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot-message">
            <div className="message-avatar">
              🤖
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Order Confirmation Modal */}
      {showOrderConfirmation && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🍕</div>
            <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Confirm Your Order</h3>
            <p style={{ margin: '0 0 2rem 0', color: '#666', lineHeight: '1.4' }}>
              To complete your pizza order, you'll need to log in for secure authentication. 
              This ensures your order details are protected.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button
                onClick={cancelOrder}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: '2px solid #ddd',
                  background: 'white',
                  color: '#666',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                Cancel
              </button>
              <button
                onClick={confirmOrder}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  background: '#2A4B3D',
                  color: 'white',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                Confirm & Login
              </button>
            </div>
          </div>
        </div>
      )}

      <form className="chatbot-input-form" onSubmit={handleSubmit} style={isEmbedded ? {
        padding: '1rem',
        borderTop: '1px solid #e9ecef',
        display: 'flex',
        gap: '0.5rem',
        alignItems: 'center',
        flexShrink: 0,
        background: 'white'
      } : {}}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isConnected ? "Ask about our menu or place an order..." : "Connecting..."}
          disabled={isLoading || !isConnected}
          className="chatbot-input"
          style={isEmbedded ? {
            flex: 1,
            borderRadius: '20px',
            border: '2px solid #e9ecef',
            padding: '0.6rem 1rem',
            fontSize: '0.9rem',
            backgroundColor: isConnected ? 'white' : '#f8f9fa'
          } : {}}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim() || !isConnected}
          className="chatbot-send-button"
          style={isEmbedded ? {
            background: isConnected 
              ? '#2A4B3D' 
              : '#6c757d',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            border: 'none',
            color: 'white',
            cursor: isConnected ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            opacity: isConnected ? 1 : 0.6
          } : {}}
        >
          ➤
        </button>
      </form>
    </div>
  );
};

export default ChatBot;