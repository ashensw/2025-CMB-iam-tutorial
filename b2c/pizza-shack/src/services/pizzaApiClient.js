/**
 * Pizza API Client for Choreo Integration
 * Handles authenticated API calls with proper scope-based authorization
 */

const PIZZA_API_BASE_URL = import.meta.env.VITE_PIZZA_API_URL || 'https://bcef7ba7-0af4-40f4-b2ad-9089f700803c-prod.e1-us-east-azure.choreoapis.dev/pizza-shack/pizza-api/v1.0';

class PizzaApiClient {
  constructor() {
    this.baseUrl = PIZZA_API_BASE_URL;
    console.log('Pizza API Client initialized with base URL:', this.baseUrl);
  }

  /**
   * Make authenticated API request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @param {string} accessToken - Bearer token
   * @returns {Promise<Response>}
   */
  async makeAuthenticatedRequest(endpoint, options = {}, accessToken) {
    if (!accessToken) {
      throw new Error('Access token is required for authenticated requests');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      'X-JWT-Assertion': accessToken,  // Add JWT assertion header for Pizza API
      ...options.headers
    };

    // Note: Choreo API key is only needed for menu calls, not for authenticated order calls

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required - please sign in');
        } else if (response.status === 403) {
          throw new Error('Insufficient permissions for this operation');
        } else {
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
      }
      
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get pizza menu (JWT token required)
   * @param {string} accessToken - Bearer token (optional for backward compatibility)
   * @returns {Promise<Object>}
   */
  async getMenu(accessToken = null) {
    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add Choreo API key header if available
      const choreoApiKey = import.meta.env.VITE_CHOREO_API_KEY;
      if (choreoApiKey) {
        headers['apikey'] = choreoApiKey;
      }
      
      // Add Authorization headers if token is provided
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
        headers['X-JWT-Assertion'] = accessToken;  // Add JWT assertion header for Pizza API
      }
      
      const response = await fetch(`${this.baseUrl}/api/menu`, {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required - please sign in');
        } else if (response.status === 403) {
          throw new Error('Insufficient permissions to access menu');
        } else {
          throw new Error(`Failed to fetch menu: ${response.status} ${response.statusText}`);
        }
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch menu:', error);
      throw error;
    }
  }

  /**
   * Get user orders
   * @param {string} accessToken - Bearer token
   * @returns {Promise<Object[]>}
   */
  async getUserOrders(accessToken) {
    if (!accessToken) {
      throw new Error('Access token is required for authenticated requests');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      'X-JWT-Assertion': accessToken,  // Add JWT assertion header for Pizza API
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/orders`, {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required - please sign in');
        } else if (response.status === 403) {
          throw new Error('Insufficient permissions for this operation');
        } else {
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get specific order
   * @param {string} orderId - Order ID
   * @param {string} accessToken - Bearer token
   * @returns {Promise<Object>}
   */
  async getOrder(orderId, accessToken) {
    const response = await this.makeAuthenticatedRequest(
      `/api/orders/${orderId}`,
      { method: 'GET' },
      accessToken
    );
    return await response.json();
  }

  /**
   * Create new order
   * @param {Object} orderData - Order data
   * @param {string} accessToken - Bearer token
   * @returns {Promise<Object>}
   */
  async createOrder(orderData, accessToken) {
    const response = await this.makeAuthenticatedRequest(
      '/api/orders',
      {
        method: 'POST',
        body: JSON.stringify(orderData)
      },
      accessToken
    );
    return await response.json();
  }

  /**
   * Get system status
   * @param {string} accessToken - Bearer token
   * @returns {Promise<Object>}
   */
  async getSystemStatus(accessToken) {
    const response = await this.makeAuthenticatedRequest(
      '/api/system/status',
      { method: 'GET' },
      accessToken
    );
    return await response.json();
  }


  /**
   * Transform cart items to API format
   * @param {Object[]} cartItems - Cart items from frontend
   * @returns {Object}
   */
  transformCartToOrderData(cartItems, customerInfo = {}) {
    const items = cartItems.map(item => ({
      menu_item_id: item.id,
      quantity: item.quantity,
      size: 'medium', // Default size
      special_instructions: item.special_instructions || ''
    }));

    return {
      items,
      customer_info: {
        name: customerInfo.name || '',
        address: customerInfo.address || '',
        contact_number: customerInfo.phone || ''
      }
    };
  }
}

// Export singleton instance
export default new PizzaApiClient();