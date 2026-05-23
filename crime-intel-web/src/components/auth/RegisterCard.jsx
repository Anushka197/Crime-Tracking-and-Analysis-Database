import RegisterForm from './RegisterForm';
import './RegisterCard.css';

/* Same geometric pattern as LoginCard — reused for visual consistency */
function GeometricPanel() {
  return (
    <svg
      className="reg-card__geo"
      viewBox="0 0 400 600"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <pattern id="reg-diamonds" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
          <polygon points="20,2 38,20 20,38 2,20" fill="none" stroke="currentColor" strokeWidth="1" />
        </pattern>
        <pattern id="reg-diamonds-lg" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
          <polygon points="40,6 74,40 40,74 6,40" fill="none" stroke="currentColor" strokeWidth="1.5" />
        </pattern>
      </defs>

      <rect width="400" height="600" fill="var(--panel-light)" />
      <rect width="400" height="600" fill="url(#reg-diamonds)"    className="reg-card__geo-sm" />
      <rect width="400" height="600" fill="url(#reg-diamonds-lg)" className="reg-card__geo-lg" />
    </svg>
  );
}

export default function RegisterCard({ onNavigateToLogin }) {
  return (
    <div className="reg-card">
      {/* Left panel — geometric pattern */}
      <div className="reg-card__left">
        <GeometricPanel />
      </div>

      {/* Accent divider */}
      <div className="reg-card__divider" />

      {/* Right panel — registration form */}
      <div className="reg-card__right">
        <RegisterForm onNavigateToLogin={onNavigateToLogin} />
      </div>
    </div>
  );
}
