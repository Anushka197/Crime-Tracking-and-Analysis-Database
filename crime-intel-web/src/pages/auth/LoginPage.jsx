import LoginCard from '../../components/auth/LoginCard';
import Header from '../../components/layout/Header';
import './LoginPage.css';

export default function LoginPage({ onNavigateToRegister }) {
  return (
    <div className="login-page">
      <Header />
      <main className="login-page__main">
        <LoginCard onNavigateToRegister={onNavigateToRegister} />
      </main>
    </div>
  );
}
