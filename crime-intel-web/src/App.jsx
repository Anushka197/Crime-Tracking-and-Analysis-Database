import { useState } from 'react';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import { useAuth } from './context/AuthContext';

export default function App() {
  const { isAuthenticated, user, logout } = useAuth();
  const [page, setPage] = useState('login');

  // Logged-in placeholder — dashboard pages will replace this
  if (isAuthenticated) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
        <p>Logged in as <strong>{user?.username}</strong></p>
        <button onClick={logout}>Log out</button>
      </div>
    );
  }

  if (page === 'register') {
    return <RegisterPage onNavigateToLogin={() => setPage('login')} />;
  }

  return <LoginPage onNavigateToRegister={() => setPage('register')} />;
}
