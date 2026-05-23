import RegisterCard from '../../components/auth/RegisterCard';
import Header from '../../components/layout/Header';
import './RegisterPage.css';

export default function RegisterPage({ onNavigateToLogin }) {
  return (
    <div className="register-page">
      <Header />
      <main className="register-page__main">
        <RegisterCard onNavigateToLogin={onNavigateToLogin} />
      </main>
    </div>
  );
}
