import React from 'react';

const OrderConfirmationModal = ({ isOpen, onClose, orderDetails, userInfo, onCreateAccount }) => {
  if (!isOpen) return null;

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
      zIndex: 5000,
      backdropFilter: 'blur(5px)'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '24px',
        width: '480px',
        maxWidth: '90vw',
        maxHeight: '85vh',
        overflow: 'auto',
        boxShadow: '0 25px 80px rgba(0, 0, 0, 0.3)',
        border: 'none',
        position: 'relative',
        animation: 'orderModalSlideIn 0.4s ease-out'
      }}>
        {/* Success Icon */}
        <div style={{
          textAlign: 'center',
          marginBottom: '20px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: '#ff6b35',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem auto',
            boxShadow: '0 8px 25px rgba(255, 107, 53, 0.3)',
            animation: 'orderSuccessPulse 1.5s ease-in-out infinite'
          }}>
            <span style={{
              fontSize: '2.5rem',
              color: 'white',
              fontWeight: 'bold'
            }}>✓</span>
          </div>
          
          <h2 style={{
            color: '#2a4b3d',
            marginBottom: '0.5rem',
            fontSize: '2rem',
            fontWeight: 'bold'
          }}>
            Order Placed Successfully!
          </h2>
          
          <p style={{
            color: '#6c757d',
            fontSize: '1.1rem',
            fontWeight: 'normal',
            margin: 0
          }}>
            Your delicious pizza is on its way!
          </p>
        </div>

        {/* Order Summary */}
        <div style={{
          background: '#F9F9F9',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '20px',
          border: '1px solid #e9ecef'
        }}>
          <h3 style={{
            color: '#2a4b3d',
            marginBottom: '1rem',
            fontSize: '1.2rem',
            textAlign: 'center'
          }}>
            Order Summary
          </h3>
          
          {/* Pizza Items List */}
          {orderDetails.items && orderDetails.items.length > 0 && (
            <div style={{
              background: 'white',
              borderRadius: '10px',
              padding: '1rem',
              marginBottom: '1rem',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                fontSize: '0.9rem',
                color: '#6c757d',
                marginBottom: '0.5rem',
                fontWeight: '500',
                textAlign: 'left'
              }}>
                Your Order:
              </div>
              {orderDetails.items.map((item, index) => (
                <div key={index} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.3rem 0',
                  borderBottom: index < orderDetails.items.length - 1 ? '1px solid #f1f3f4' : 'none'
                }}>
                  <div style={{
                    color: '#2a4b3d',
                    fontSize: '0.95rem'
                  }}>
                    {item.name}
                  </div>
                  <div style={{
                    color: '#D96F32',
                    fontSize: '0.9rem',
                    fontWeight: '500'
                  }}>
                    ${item.price}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1rem',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{
              fontSize: '0.9rem',
              color: '#6c757d',
              marginBottom: '0.5rem',
              fontWeight: '500',
              textAlign: 'left'
            }}>
              Total Amount:
            </div>
            <div style={{
              fontSize: '1.4rem',
              fontWeight: 'bold',
              color: '#D96F32',
              textAlign: 'left'
            }}>
              ${orderDetails.total}
            </div>
          </div>

          {userInfo?.address && (
            <div style={{
              background: 'white',
              borderRadius: '10px',
              padding: '1rem',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                fontSize: '0.9rem',
                color: '#6c757d',
                marginBottom: '0.3rem'
              }}>
                Delivery Address:
              </div>
              <div style={{
                fontSize: '1rem',
                color: '#2a4b3d',
                fontWeight: '500'
              }}>
                📍 {userInfo.address}
                {userInfo.city && `, ${userInfo.city}`}
                {userInfo.zipCode && ` ${userInfo.zipCode}`}
              </div>
            </div>
          )}
        </div>

        {/* Horizontal Divider */}
        <hr style={{
          border: 'none',
          borderTop: '1px solid #e9ecef',
          margin: '20px 0',
          opacity: 0.5
        }} />

        {/* Unified Bottom Action Section */}
        <div style={{
          textAlign: 'center'
        }}>
          {/* Delivery Time as Simple Text */}
          <div style={{
            fontSize: '1rem',
            color: '#2a4b3d',
            fontWeight: '600',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}>
            <span>⏱️</span>
            <span>Estimated Delivery Time: 25-35 minutes</span>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px'
          }}>
            {!orderDetails.isAuthenticated ? (
              <>
                {onCreateAccount && (
                  <button
                    onClick={() => {
                      onClose();
                      onCreateAccount();
                    }}
                    style={{
                      background: '#ff6b35',
                      color: 'white',
                      border: 'none',
                      padding: '12px 32px',
                      borderRadius: '9999px',
                      fontSize: '1rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 15px rgba(255, 107, 53, 0.3)',
                      width: '100%',
                      maxWidth: '280px'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 6px 20px rgba(255, 107, 53, 0.4)';
                      e.target.style.background = '#e85a2e';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 15px rgba(255, 107, 53, 0.3)';
                      e.target.style.background = '#ff6b35';
                    }}
                  >
                    Create Account & Track Order
                  </button>
                )}
                <button
                  onClick={onClose}
                  style={{
                    background: '#2a4b3d',
                    color: 'white',
                    border: 'none',
                    padding: '12px 32px',
                    borderRadius: '9999px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 4px 15px rgba(44, 62, 80, 0.3)',
                    width: '100%',
                    maxWidth: '280px'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(44, 62, 80, 0.4)';
                    e.target.style.background = '#34495e';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(44, 62, 80, 0.3)';
                    e.target.style.background = '#2a4b3d';
                  }}
                >
                  Continue as Guest
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={onClose}
                  style={{
                    background: '#ff6b35',
                    color: 'white',
                    border: 'none',
                    padding: '12px 32px',
                    borderRadius: '9999px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 4px 15px rgba(255, 107, 53, 0.3)',
                    width: '100%',
                    maxWidth: '280px'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(255, 107, 53, 0.4)';
                    e.target.style.background = '#e85a2e';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(255, 107, 53, 0.3)';
                    e.target.style.background = '#ff6b35';
                  }}
                >
                  Track My Order
                </button>
                <button
                  onClick={onClose}
                  style={{
                    background: '#2a4b3d',
                    color: 'white',
                    border: 'none',
                    padding: '12px 32px',
                    borderRadius: '9999px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 4px 15px rgba(44, 62, 80, 0.3)',
                    width: '100%',
                    maxWidth: '280px'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(44, 62, 80, 0.4)';
                    e.target.style.background = '#34495e';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(44, 62, 80, 0.3)';
                    e.target.style.background = '#2a4b3d';
                  }}
                >
                  Back to Menu
                </button>
              </>
            )}
          </div>
        </div>


        <style>
          {`
            @keyframes orderModalSlideIn {
              from {
                opacity: 0;
                transform: translateY(-30px) scale(0.95);
              }
              to {
                opacity: 1;
                transform: translateY(0) scale(1);
              }
            }
            
            @keyframes orderSuccessPulse {
              0%, 100% {
                transform: scale(1);
                box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
              }
              50% {
                transform: scale(1.05);
                box-shadow: 0 12px 35px rgba(255, 107, 53, 0.5);
              }
            }
          `}
        </style>
      </div>
    </div>
  );
};

export default OrderConfirmationModal;