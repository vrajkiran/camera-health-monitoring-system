import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthState, User, UserRole, LoginResponse } from '../types/auth';
import { clearStoredAuth, getStoredToken, setStoredToken } from '../services/api';

interface AuthContextType extends AuthState {
  login: (username: string, password: string, remember?: boolean) => Promise<void>;
  logout: () => void;
  dismissSessionExpired: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const USER_STORAGE_KEY = 'surveillance_auth_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const token = getStoredToken();
    const savedUser = localStorage.getItem(USER_STORAGE_KEY) || sessionStorage.getItem(USER_STORAGE_KEY);
    let user: User | null = null;
    let role: UserRole = 'VIEWER';

    if (savedUser) {
      try {
        user = JSON.parse(savedUser);
        role = user?.role || 'VIEWER';
      } catch {
        // Fallback if malformed
      }
    }

    return {
      token,
      user,
      role,
      isAuthenticated: !!token,
      isLoading: false,
      sessionExpired: false,
    };
  });

  // Verify token on mount if present
  useEffect(() => {
    const verifyToken = async () => {
      const token = getStoredToken();
      if (!token) return;

      try {
        const response = await fetch('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          const user: User = data.user || {
            username: data.username || 'admin',
            role: data.role || 'ADMINISTRATOR',
            display_name: data.display_name || data.username,
          };
          setAuthState((prev) => ({
            ...prev,
            user,
            role: user.role,
            isAuthenticated: true,
          }));
        } else if (response.status === 401) {
          clearStoredAuth();
          setAuthState((prev) => ({
            ...prev,
            token: null,
            user: null,
            role: 'VIEWER',
            isAuthenticated: false,
            sessionExpired: true,
          }));
        }
      } catch (err) {
        console.error('Error verifying auth token:', err);
      }
    };

    verifyToken();
  }, []);

  // Listen for global session expiration events (e.g. from 401 API responses)
  useEffect(() => {
    const handleExpired = () => {
      setAuthState((prev) => ({
        ...prev,
        token: null,
        user: null,
        isAuthenticated: false,
        sessionExpired: true,
      }));
    };

    window.addEventListener('session-expired', handleExpired);
    return () => window.removeEventListener('session-expired', handleExpired);
  }, []);

  const login = async (username: string, password: string, remember: boolean = true) => {
    setAuthState((prev) => ({ ...prev, isLoading: true, sessionExpired: false }));

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data: LoginResponse = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || 'Authentication failed. Please verify credentials.');
      }

      const user: User = data.user || {
        username,
        role: data.role || 'VIEWER',
        display_name: username,
      };

      setStoredToken(data.token, remember);
      const userStr = JSON.stringify(user);
      if (remember) {
        localStorage.setItem(USER_STORAGE_KEY, userStr);
      } else {
        sessionStorage.setItem(USER_STORAGE_KEY, userStr);
      }

      setAuthState({
        token: data.token,
        user,
        role: user.role,
        isAuthenticated: true,
        isLoading: false,
        sessionExpired: false,
      });
    } catch (err) {
      setAuthState((prev) => ({ ...prev, isLoading: false }));
      throw err;
    }
  };

  const logout = () => {
    clearStoredAuth();
    setAuthState({
      token: null,
      user: null,
      role: 'VIEWER',
      isAuthenticated: false,
      isLoading: false,
      sessionExpired: false,
    });
  };

  const dismissSessionExpired = () => {
    setAuthState((prev) => ({ ...prev, sessionExpired: false }));
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        logout,
        dismissSessionExpired,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
