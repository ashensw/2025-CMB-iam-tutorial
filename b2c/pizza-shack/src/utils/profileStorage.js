const PROFILE_KEY = 'pizza_shack_profile_id';
const PROFILE_EXPIRY_KEY = 'pizza_shack_profile_expiry';
const DEFAULT_EXPIRY_DAYS = parseInt(import.meta.env.VITE_PROFILE_EXPIRY_DAYS) || 90;

class ProfileStorage {
  constructor() {
    this.storageAvailable = this.checkStorageAvailability();
  }

  checkStorageAvailability() {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, 'test');
      localStorage.removeItem(test);
      return true;
    } catch {
      console.warn('localStorage not available, falling back to sessionStorage');
      try {
        const test = '__storage_test__';
        sessionStorage.setItem(test, 'test');
        sessionStorage.removeItem(test);
        return 'session';
      } catch {
        console.warn('sessionStorage not available, falling back to memory');
        return false;
      }
    }
  }

  getStorage() {
    if (this.storageAvailable === true) {
      return localStorage;
    } else if (this.storageAvailable === 'session') {
      return sessionStorage;
    }
    return null;
  }

  storeProfileId(profileId, expiryDays = DEFAULT_EXPIRY_DAYS) {
    if (!profileId) {
      console.error('Profile ID is required');
      return false;
    }

    try {
      const storage = this.getStorage();
      
      if (storage) {
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + expiryDays);
        
        storage.setItem(PROFILE_KEY, profileId);
        storage.setItem(PROFILE_EXPIRY_KEY, expiryDate.toISOString());
        
        console.log('Profile ID stored successfully:', profileId);
        return true;
      } else {
        this.memoryStorage = this.memoryStorage || {};
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + expiryDays);
        
        this.memoryStorage[PROFILE_KEY] = profileId;
        this.memoryStorage[PROFILE_EXPIRY_KEY] = expiryDate.toISOString();
        
        console.log('Profile ID stored in memory:', profileId);
        return true;
      }
    } catch (error) {
      console.error('Failed to store profile ID:', error);
      return false;
    }
  }

  getStoredProfileId() {
    try {
      const storage = this.getStorage();
      let profileId, expiryString;
      
      if (storage) {
        profileId = storage.getItem(PROFILE_KEY);
        expiryString = storage.getItem(PROFILE_EXPIRY_KEY);
      } else if (this.memoryStorage) {
        profileId = this.memoryStorage[PROFILE_KEY];
        expiryString = this.memoryStorage[PROFILE_EXPIRY_KEY];
      }

      if (!profileId || !expiryString) {
        return null;
      }

      const expiryDate = new Date(expiryString);
      const now = new Date();

      if (now > expiryDate) {
        console.log('Profile ID expired, removing from storage');
        this.removeProfileId();
        return null;
      }

      console.log('Retrieved valid profile ID:', profileId);
      return profileId;
    } catch (error) {
      console.error('Failed to retrieve profile ID:', error);
      return null;
    }
  }

  removeProfileId() {
    try {
      const storage = this.getStorage();
      
      if (storage) {
        storage.removeItem(PROFILE_KEY);
        storage.removeItem(PROFILE_EXPIRY_KEY);
      }
      
      if (this.memoryStorage) {
        delete this.memoryStorage[PROFILE_KEY];
        delete this.memoryStorage[PROFILE_EXPIRY_KEY];
      }
      
      console.log('Profile ID removed from storage');
      return true;
    } catch (error) {
      console.error('Failed to remove profile ID:', error);
      return false;
    }
  }

  isProfileIdValid() {
    const profileId = this.getStoredProfileId();
    return profileId !== null;
  }

  getProfileInfo() {
    try {
      const storage = this.getStorage();
      let profileId, expiryString;
      
      if (storage) {
        profileId = storage.getItem(PROFILE_KEY);
        expiryString = storage.getItem(PROFILE_EXPIRY_KEY);
      } else if (this.memoryStorage) {
        profileId = this.memoryStorage[PROFILE_KEY];
        expiryString = this.memoryStorage[PROFILE_EXPIRY_KEY];
      }

      if (!profileId || !expiryString) {
        return null;
      }

      return {
        profileId,
        expiryDate: new Date(expiryString),
        isValid: new Date() <= new Date(expiryString),
        storageType: this.storageAvailable === true ? 'localStorage' : 
                     this.storageAvailable === 'session' ? 'sessionStorage' : 'memory'
      };
    } catch (error) {
      console.error('Failed to get profile info:', error);
      return null;
    }
  }

  extendExpiry(additionalDays = DEFAULT_EXPIRY_DAYS) {
    const profileId = this.getStoredProfileId();
    if (profileId) {
      return this.storeProfileId(profileId, additionalDays);
    }
    return false;
  }

  clearExpiredProfiles() {
    const profileInfo = this.getProfileInfo();
    if (profileInfo && !profileInfo.isValid) {
      this.removeProfileId();
      return true;
    }
    return false;
  }
}

export default new ProfileStorage();