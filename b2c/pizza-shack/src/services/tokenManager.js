/**
 * Token Management Service
 * Handles secure token storage, refresh, and validation
 */

class TokenManager {
  constructor() {
    this.tokenKey = 'pizza_shack_token';
    this.expiryKey = 'pizza_shack_token_expiry';
    this.refreshTokenKey = 'pizza_shack_refresh_token';
  }

  /**
   * Store access token securely
   * @param {string} accessToken - Access token
   * @param {number} expiresIn - Token expiry in seconds
   * @param {string} refreshToken - Refresh token (optional)
   */
  storeToken(accessToken, expiresIn = 3600, refreshToken = null) {
    const expiryTime = Date.now() + (expiresIn * 1000);
    
    try {
      // Store in sessionStorage for better security (cleared on tab close)
      sessionStorage.setItem(this.tokenKey, accessToken);
      sessionStorage.setItem(this.expiryKey, expiryTime.toString());
      
      if (refreshToken) {
        // Store refresh token in localStorage for persistence
        localStorage.setItem(this.refreshTokenKey, refreshToken);
      }
      
      console.log('Token stored successfully');
    } catch (error) {
      console.error('Failed to store token:', error);
      throw new Error('Token storage failed');
    }
  }

  /**
   * Get stored access token
   * @returns {string|null}
   */
  getAccessToken() {
    try {
      const token = sessionStorage.getItem(this.tokenKey);
      
      if (!token) {
        return null;
      }

      // Check if token is expired
      if (this.isTokenExpired()) {
        this.clearToken();
        return null;
      }

      return token;
    } catch (error) {
      console.error('Failed to retrieve token:', error);
      return null;
    }
  }


  /**
   * Get refresh token
   * @returns {string|null}
   */
  getRefreshToken() {
    try {
      return localStorage.getItem(this.refreshTokenKey);
    } catch (error) {
      console.error('Failed to retrieve refresh token:', error);
      return null;
    }
  }

  /**
   * Check if token is expired
   * @returns {boolean}
   */
  isTokenExpired() {
    try {
      const expiryTime = sessionStorage.getItem(this.expiryKey);
      if (!expiryTime) {
        return true;
      }
      
      return Date.now() >= parseInt(expiryTime);
    } catch (error) {
      console.error('Failed to check token expiry:', error);
      return true;
    }
  }

  /**
   * Get time until token expires
   * @returns {number} Seconds until expiry, or 0 if expired
   */
  getTimeToExpiry() {
    try {
      const expiryTime = sessionStorage.getItem(this.expiryKey);
      if (!expiryTime) {
        return 0;
      }
      
      const timeLeft = parseInt(expiryTime) - Date.now();
      return Math.max(0, Math.floor(timeLeft / 1000));
    } catch (error) {
      console.error('Failed to calculate time to expiry:', error);
      return 0;
    }
  }


  /**
   * Clear all stored tokens
   */
  clearToken() {
    try {
      sessionStorage.removeItem(this.tokenKey);
      sessionStorage.removeItem(this.expiryKey);
      localStorage.removeItem(this.refreshTokenKey);
      console.log('Tokens cleared successfully');
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  /**
   * Refresh access token using refresh token
   * @param {Function} refreshCallback - Function to call for token refresh
   * @returns {Promise<string>} New access token
   */
  async refreshAccessToken(refreshCallback) {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const tokenResponse = await refreshCallback(refreshToken);
      
      this.storeToken(
        tokenResponse.access_token,
        tokenResponse.expires_in,
        tokenResponse.refresh_token || refreshToken
      );
      
      return tokenResponse.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearToken();
      throw error;
    }
  }

  /**
   * Get token info for debugging
   * @returns {Object}
   */
  getTokenInfo() {
    return {
      hasToken: !!this.getAccessToken(),
      isExpired: this.isTokenExpired(),
      timeToExpiry: this.getTimeToExpiry()
    };
  }
}

// Export singleton instance
export default new TokenManager();