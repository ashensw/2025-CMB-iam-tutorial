import React from 'react';

const PersonalizedRecommendations = ({ recommendations, pizzaMenu, onAddToCart }) => {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  const findPizzaByName = (name) => {
    return pizzaMenu.find(pizza => 
      pizza.name.toLowerCase().includes(name.toLowerCase()) ||
      name.toLowerCase().includes(pizza.name.toLowerCase())
    );
  };

  return (
    <div style={{
      marginBottom: '2rem',
      padding: '1.5rem',
      background: '#E6F3EE',
      borderRadius: '15px',
      border: '2px solid #2A4B3D',
      boxShadow: '0 4px 15px rgba(42, 75, 61, 0.1)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '1rem',
        justifyContent: 'center'
      }}>
        <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>✨</span>
        <h3 style={{
          color: '#2A4B3D',
          margin: 0,
          fontSize: '1.3rem',
          fontWeight: 'bold'
        }}>
          Recommended for You
        </h3>
        <span style={{ fontSize: '1.5rem', marginLeft: '0.5rem' }}>✨</span>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        {recommendations.map((rec, index) => {
          const pizza = findPizzaByName(rec.subtitle);
          
          return (
            <div key={index} style={{
              background: 'rgba(255, 255, 255, 0.9)',
              borderRadius: '10px',
              padding: '1rem',
              border: '1px solid rgba(255, 107, 53, 0.2)',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-3px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(255, 107, 53, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}>
              {pizza && (
                <img 
                  src={pizza.img} 
                  alt={pizza.name}
                  style={{
                    width: '60px',
                    height: '60px',
                    objectFit: 'cover',
                    borderRadius: '50%',
                    marginBottom: '0.5rem',
                    border: '2px solid #2A4B3D'
                  }}
                />
              )}
              
              <div style={{
                fontSize: '0.8rem',
                color: '#D96F32',
                fontWeight: 'bold',
                marginBottom: '0.3rem'
              }}>
                {rec.title}
              </div>
              
              <div style={{
                fontSize: '0.9rem',
                color: '#2a4b3d',
                marginBottom: '0.8rem',
                fontWeight: '500'
              }}>
                {rec.subtitle}
              </div>
              
              {pizza && (
                <button
                  onClick={() => onAddToCart(pizza)}
                  style={{
                    background: '#D96F32',
                    color: 'white',
                    border: 'none',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '15px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    transition: 'transform 0.2s ease',
                    width: '100%'
                  }}
                  onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                >
                  {rec.action || 'Add to Cart'}
                </button>
              )}
            </div>
          );
        })}
      </div>
      
    </div>
  );
};

export default PersonalizedRecommendations;