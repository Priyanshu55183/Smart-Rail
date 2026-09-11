'use client';

/**
 * Auth Context Provider
 * =====================
 * Manages authentication state across the entire app.
 * 
 * Provides:
 * - user: Current logged-in user (or null)
 * - token: JWT access token (or null)
 * - loading: True while checking auth on mount
 * - login(email, password): Authenticate and store JWT
 * - register(name, email, password): Create account and store JWT
 * - logout(): Clear JWT and user state
 * - fetchWithAuth(url, options): Fetch wrapper with Authorization header
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

/**
 * API base — empty string in browser (uses Next.js rewrite proxy)
 */
function getApiBase() {
  return '';
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * On mount, check if a JWT exists in localStorage
   * and validate it by calling /api/auth/me
   */
  useEffect(() => {
    const savedToken = localStorage.getItem('smartrail_token');
    if (savedToken) {
      setToken(savedToken);
      // Validate the token by fetching the user profile
      fetch(`${getApiBase()}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${savedToken}` },
      })
        .then((res) => {
          if (res.ok) return res.json();
          throw new Error('Invalid token');
        })
        .then((userData) => {
          setUser(userData);
          setLoading(false);
        })
        .catch(() => {
          // Token expired or invalid — clear it
          localStorage.removeItem('smartrail_token');
          setToken(null);
          setUser(null);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  /**
   * Register a new account
   */
  const register = useCallback(async (name, email, password) => {
    const res = await fetch(`${getApiBase()}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed');
    }

    // Store token and user
    localStorage.setItem('smartrail_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);

    return data;
  }, []);

  /**
   * Login with email and password
   */
  const login = useCallback(async (email, password) => {
    const res = await fetch(`${getApiBase()}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    // Store token and user
    localStorage.setItem('smartrail_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);

    return data;
  }, []);

  /**
   * Logout — clear token and user state
   */
  const logout = useCallback(() => {
    localStorage.removeItem('smartrail_token');
    setToken(null);
    setUser(null);
  }, []);

  /**
   * Fetch wrapper that auto-attaches the Authorization header.
   * Use this for any API call that requires authentication.
   */
  const fetchWithAuth = useCallback(async (url, options = {}) => {
    const currentToken = localStorage.getItem('smartrail_token');
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(currentToken ? { 'Authorization': `Bearer ${currentToken}` } : {}),
        ...options.headers,
      },
    });
    return res;
  }, []);

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    fetchWithAuth,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access auth context from any component.
 * Usage: const { user, login, logout } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
