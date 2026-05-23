import { useState } from 'react';
import { Eye, EyeOff, User, Lock, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { loginUser } from '../../services/api';
import './LoginForm.css';

export default function LoginForm({ onNavigateToRegister }) {
  const { login } = useAuth();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('Please enter both username and password.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const data = await loginUser({
        username: formData.username.trim(),
        password: formData.password,
      });
      // Store token + minimal user info from the JWT response
      // The API returns: { access_token, token_type, expires_at }
      // We decode the username from the form since the login response doesn't include user details
      login(data.access_token, {
        username: formData.username.trim(),
        expires_at: data.expires_at,
      });
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    // Placeholder — password reset page not yet built
  };

  return (
    <div className="login-form__wrapper">
      {/* Headings */}
      <div>
        <h2 className="login-form__heading">Crime Records Portal</h2>
        <p className="login-form__subheading">
          Authorized Personnel &amp; Citizen Inquiry Login
        </p>
      </div>

      {/* Divider */}
      <div className="login-form__divider" />

      {/* Form */}
      <form onSubmit={handleSubmit} className="login-form" noValidate>

        {/* Error slot — always reserves space, visible only when error exists */}
        <div className="login-form__error-slot">
          {error && (
            <div className="login-form__error" role="alert">
              <AlertCircle size={14} className="login-form__error-icon" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Username */}
        <div className="login-form__field">
          <label htmlFor="username" className="login-form__label">
            Username / Registry ID
          </label>
          <div className="login-form__input-wrapper">
            <span className="login-form__input-icon">
              <User size={15} />
            </span>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter Registry ID or Username"
              className="login-form__input"
            />
          </div>
        </div>

        {/* Password */}
        <div className="login-form__field">
          <label htmlFor="password" className="login-form__label">
            Password
          </label>
          <div className="login-form__input-wrapper">
            <span className="login-form__input-icon">
              <Lock size={15} />
            </span>
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter Password"
              className="login-form__input login-form__input--password"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="login-form__eye-btn"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        {/* Forgot password */}
        <div className="login-form__forgot-row">
          <a href="#" onClick={handleForgotPassword} className="login-form__forgot-link">
            Forgot Password?
          </a>
        </div>

        {/* Login button */}
        <button type="submit" disabled={isLoading} className="login-form__btn-primary">
          {isLoading ? 'Verifying…' : 'Log In'}
        </button>

        {/* Register button */}
        <button type="button" onClick={onNavigateToRegister} className="login-form__btn-secondary">
          Register a New Account
        </button>
      </form>

      {/* Footer note */}
      <p className="login-form__footer-note">
        Unauthorised access is a criminal offence under the IT Act, 2000.
      </p>
    </div>
  );
}
