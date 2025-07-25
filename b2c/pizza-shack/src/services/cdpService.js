const DEFAULT_CDP_BASE_URL = 'https://bcef7ba7-0af4-40f4-b2ad-9089f700803c-dev.e1-us-east-azure.choreoapis.dev/default/iam-cdm/v1.0';

class CDPService {
  constructor() {
    this.baseURL = import.meta.env.VITE_CDP_BASE_URL || DEFAULT_CDP_BASE_URL;
    this.isEnabled = this.getEnvConfig();
    this.debugMode = import.meta.env.VITE_CDP_DEBUG === 'true';
    
    if (this.debugMode) {
      console.log('CDP Service initialized:', {
        baseURL: this.baseURL,
        enabled: this.isEnabled,
        debugMode: this.debugMode
      });
    }
  }

  getEnvConfig() {
    const enabled = import.meta.env.VITE_CDP_ENABLED;
    return enabled === undefined || enabled === 'true';
  }

  async createProfile(profileData) {
    if (!this.isEnabled) {
      if (this.debugMode) console.log('CDP service is disabled');
      return null;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(`${this.baseURL}/profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      if (this.debugMode) console.log('CDP Profile created successfully:', result);
      return result;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.warn('CDP profile creation timed out');
        return null;
      }
      
      console.warn('CDP profile creation failed (non-fatal):', error.message);
      
      // Return null for graceful degradation instead of throwing
      return null;
    }
  }

  async getProfile(profileId) {
    if (!this.isEnabled) {
      if (this.debugMode) console.log('CDP service is disabled');
      return null;
    }

    if (!profileId) {
      console.warn('Profile ID is required for retrieval');
      return null;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout

      const response = await fetch(`${this.baseURL}/profiles/${profileId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 404) {
          if (this.debugMode) console.log('Profile not found:', profileId);
          return null;
        }
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      if (this.debugMode) console.log('CDP Profile retrieved successfully:', result);
      return result;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.warn('CDP profile retrieval timed out');
        return null;
      }
      
      console.warn('CDP profile retrieval failed (non-fatal):', error.message);
      return null;
    }
  }

  async updateProfile(profileId, updateData) {
    if (!this.isEnabled) {
      console.log('CDP service is disabled');
      return null;
    }

    if (!profileId) {
      throw new Error('Profile ID is required');
    }

    try {
      const response = await fetch(`${this.baseURL}/profiles/${profileId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        throw new Error(`Failed to update profile: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('CDP Profile updated successfully:', result);
      return result;
    } catch (error) {
      console.error('Error updating CDP profile:', error);
      throw error;
    }
  }

  formatOrderData(cart, userInfo) {
    // Convert all cart items to order array
    const orderArray = cart.map(item => ({
      item: item.name || 'unknown',
      size: this.extractSize(item.name) || 'm',
      quantity: item.quantity?.toString() || '1'
    }));

    return {
      identity_attributes: {
        emailaddress: userInfo.email,
        displayName: userInfo.name,
        mobile: userInfo.phone || userInfo.mobile || ''
      },
      traits: {
        order: orderArray
      }
    };
  }

  extractSize(pizzaName) {
    const lowerName = pizzaName.toLowerCase();
    if (lowerName.includes('small')) return 's';
    if (lowerName.includes('large')) return 'l';
    if (lowerName.includes('extra') || lowerName.includes('xl')) return 'xl';
    return 'm';
  }

  formatRecommendations(profileData) {
    if (!profileData || !profileData.traits || !profileData.traits.order || !Array.isArray(profileData.traits.order)) {
      return [];
    }

    const orderArray = profileData.traits.order;
    const recommendations = [];
    
    // Create recommendations based on previously ordered items
    // Get unique items to avoid duplicates
    const uniqueItems = [];
    const seenItems = new Set();
    
    orderArray.forEach(orderItem => {
      if (!seenItems.has(orderItem.item)) {
        uniqueItems.push(orderItem);
        seenItems.add(orderItem.item);
      }
    });
    
    // Create recommendation for each unique item (limit to 3)
    uniqueItems.slice(0, 3).forEach(orderItem => {
      recommendations.push({
        type: 'previous_order',
        title: `You loved this before!`,
        subtitle: orderItem.item,
        action: 'Order Again',
        size: orderItem.size,
        quantity: orderItem.quantity
      });
    });

    return recommendations;
  }
}

export default new CDPService();