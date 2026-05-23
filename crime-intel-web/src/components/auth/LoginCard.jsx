import LoginForm from './LoginForm';
import './LoginCard.css';

/* Simple geometric pattern — diagonal grid of crimson diamonds on the light panel */
function GeometricPanel() {
  return (
    <svg
      className="login-card__geo"
      viewBox="0 0 400 540"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        {/* Repeating diamond tile */}
        <pattern id="diamonds" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
          <polygon points="20,2 38,20 20,38 2,20" fill="none" stroke="currentColor" strokeWidth="1" />
        </pattern>
        {/* Larger sparse diamonds layered on top */}
        <pattern id="diamonds-lg" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
          <polygon points="40,6 74,40 40,74 6,40" fill="none" stroke="currentColor" strokeWidth="1.5" />
        </pattern>
      </defs>

      {/* Base fill */}
      <rect width="400" height="540" fill="var(--panel-light)" />

      {/* Small diamond grid */}
      <rect width="400" height="540" fill="url(#diamonds)" className="login-card__geo-sm" />

      {/* Large diamond grid */}
      <rect width="400" height="540" fill="url(#diamonds-lg)" className="login-card__geo-lg" />

    </svg>
  );
}

export default function LoginCard({ onNavigateToRegister }) {
  return (
    <div className="login-card">
      {/* Left panel — geometric pattern */}
      <div className="login-card__left">
        <GeometricPanel />
      </div>

      {/* Accent divider */}
      <div className="login-card__divider" />

      {/* Right panel — login form */}
      <div className="login-card__right">
        <LoginForm onNavigateToRegister={onNavigateToRegister} />
      </div>
    </div>
  );
}
