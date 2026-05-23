/**
 * AuthContext.jsx
 * ---------------
 * Provides authentication state to the entire app.
 *
 * Stored in localStorage:
 *   access_token  — raw JWT string
 *   auth_user     — JSON-serialised { user_id, username, email, role, is_active }
 *
 * Exposed via useAuth():
 *   user          — current user object or null
 *   token         — JWT string or null
 *   login(token, user) — persist session
 *   logout()           — clear session
 *   isAuthenticated    — boolean shorthand
 */

import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

function loadStoredUser() {
  try {
    const raw = localStorage.getItem('auth_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [user, setUser]   = useState(loadStoredUser);

  const login = (newToken, newUser) => {
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('auth_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
