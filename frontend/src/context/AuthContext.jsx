import React, { createContext, useState, useContext, useEffect } from 'react';

/**
 * Authentication Context
 * Manages JWT token and user authentication state
 */

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load user info on mount if token exists
  useEffect(() => {
    if (token) {
      fetchUserInfo();
    }
  }, [token]);

  /**
   * Fetch current user info from backend
   */
  const fetchUserInfo = async (tokenToUse = null) => {
    const authToken = tokenToUse || token;
    if (!authToken) {
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token invalid, clear it
        logout();
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      logout();
    }
  };

  /**
   * Login function
   */
  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        const newToken = data.access_token;
        setToken(newToken);
        localStorage.setItem('token', newToken);
        // Use the token directly instead of waiting for state update
        await fetchUserInfo(newToken);
        setIsLoading(false);
        return { success: true };
      } else {
        setIsLoading(false);
        return { success: false, error: data.detail || 'Login failed' };
      }
    } catch (error) {
      setIsLoading(false);
      return { success: false, error: error.message };
    }
  };

  /**
   * Signup function
   */
  const signup = async (name, email, password) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();

      if (response.ok) {
        // After signup, automatically login
        // Small delay to ensure database write is complete
        await new Promise(resolve => setTimeout(resolve, 100));
        const loginResult = await login(email, password);
        setIsLoading(false);
        return loginResult;
      } else {
        setIsLoading(false);
        return { success: false, error: data.detail || 'Signup failed' };
      }
    } catch (error) {
      setIsLoading(false);
      return { success: false, error: error.message };
    }
  };

  /**
   * Logout function
   */
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  /**
   * Get authorization header for API calls
   */
  const getAuthHeader = () => {
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const value = {
    token,
    user,
    isLoading,
    login,
    signup,
    logout,
    isAuthenticated: !!token,
    getAuthHeader
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
