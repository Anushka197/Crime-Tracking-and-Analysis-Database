import { useState } from 'react';
import { User, Mail, Phone, Shield, Lock, Eye, EyeOff, KeyRound } from 'lucide-react';
import { registerUser } from '../../services/api';
import './RegisterForm.css';

const ROLES = [
  { value: 'viewer',  label: 'Viewer'  },
  { value: 'officer', label: 'Officer' },
  { value: 'judge',   label: 'Judge'   },
  { value: 'admin',   label: 'Admin'   },
];

const RESTRICTED_ROLES = ['officer', 'judge', 'admin'];

const VALID_CODES = {
  officer: 'OFFICER-2024',
  judge:   'JUDGE-2024',
  admin:   'ADMIN-2024',
};

const INITIAL_FORM = {
  username:         '',
  email:            '',
  mobile_number:    '',
  role:             'viewer',
  reg_code:         '',
  password:         '',
  confirm_password: '',
};

/* Per-field validation rules — return error string or null */
const VALIDATORS = {
  username: (v) => {
    if (!v.trim())       return 'Username is required.';
    if (v.length < 3)    return 'Must be at least 3 characters.';
    if (v.length > 100)  return 'Must be 100 characters or fewer.';
    return null;
  },
  email: (v) => {
    if (!v.trim()) return 'Email is required.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'Enter a valid email address.';
    return null;
  },
  mobile_number: (v) => {
    if (!v) return null; // optional
    const digits = v.replace(/\D/g, '');
    if (digits.length !== 10) return 'Must be exactly 10 digits.';
    return null;
  },
  password: (v) => {
    if (!v)           return 'Password is required.';
    if (v.length < 8) return 'Must be at least 8 characters.';
    return null;
  },
  confirm_password: (v, form) => {
    if (!v)                  return 'Please confirm your password.';
    if (v !== form.password) return 'Passwords do not match.';
    return null;
  },
  reg_code: (v, form) => {
    if (!RESTRICTED_ROLES.includes(form.role)) return null;
    if (!v.trim()) return 'Registration code is required.';
    if (v.trim() !== VALID_CODES[form.role])   return 'Invalid registration code.';
    return null;
  },
};

export default function RegisterForm({ onNavigateToLogin }) {
  const [formData, setFormData]         = useState(INITIAL_FORM);
  const [fieldErrors, setFieldErrors]   = useState({});
  const [touched, setTouched]           = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm]   = useState(false);
  const [submitError, setSubmitError]   = useState('');
  const [isLoading, setIsLoading]       = useState(false);

  const requiresCode = RESTRICTED_ROLES.includes(formData.role);

  /* Validate a single field and update fieldErrors */
  const validateField = (name, value, currentForm) => {
    const validator = VALIDATORS[name];
    if (!validator) return null;
    const error = validator(value, currentForm);
    setFieldErrors((prev) => ({ ...prev, [name]: error }));
    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...formData, [name]: value };
    setFormData(updated);
    setSubmitError('');
    // Only show inline error once the field has been touched
    if (touched[name]) validateField(name, value, updated);
    // Re-validate confirm_password live when password changes
    if (name === 'password' && touched['confirm_password']) {
      validateField('confirm_password', updated.confirm_password, updated);
    }
  };

  const handleRoleChange = (e) => {
    const updated = { ...formData, role: e.target.value, reg_code: '' };
    setFormData(updated);
    setSubmitError('');
    setFieldErrors((prev) => ({ ...prev, reg_code: null }));
    setTouched((prev) => ({ ...prev, reg_code: false }));
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    validateField(name, value, formData);
  };

  /* Validate all fields at once on submit */
  const validateAll = () => {
    const fields = ['username', 'email', 'mobile_number', 'password', 'confirm_password'];
    if (requiresCode) fields.push('reg_code');

    const errors = {};
    let hasError = false;
    for (const name of fields) {
      const validator = VALIDATORS[name];
      if (!validator) continue;
      const error = validator(formData[name], formData);
      errors[name] = error;
      if (error) hasError = true;
    }
    setFieldErrors(errors);
    // Mark all as touched so errors show
    const allTouched = fields.reduce((acc, f) => ({ ...acc, [f]: true }), {});
    setTouched((prev) => ({ ...prev, ...allTouched }));
    return !hasError;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateAll()) return;

    setIsLoading(true);
    setSubmitError('');

    try {
      // Send only the fields the backend accepts — role is assigned server-side
      const payload = {
        username:         formData.username.trim(),
        email:            formData.email.trim(),
        password:         formData.password,
        confirm_password: formData.confirm_password,
        ...(formData.mobile_number.trim() && { mobile_number: formData.mobile_number.trim() }),
      };

      await registerUser(payload);
      // On success navigate back to login
      onNavigateToLogin();
    } catch (err) {
      setSubmitError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /* Shared props for blur handling */
  const blurProps = { onBlur: handleBlur };

  return (
    <div className="reg-form__wrapper">

      <div>
        <h2 className="reg-form__heading">Create Account</h2>
        <p className="reg-form__subheading">Crime Records Portal — New User Registration</p>
      </div>

      <div className="reg-form__divider" />

      <form onSubmit={handleSubmit} className="reg-form" noValidate>

        {/* Top-level submit error (e.g. network / server) */}
        {submitError && (
          <p className="reg-form__submit-error" role="alert">{submitError}</p>
        )}

        {/* Row: Username + Email */}
        <div className="reg-form__row">
          <Field label="Username" htmlFor="username" error={touched.username && fieldErrors.username}>
            <InputWrapper icon={<User size={15} />}>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                value={formData.username}
                onChange={handleChange}
                {...blurProps}
                placeholder="Choose a username"
                className={inputClass(touched.username && fieldErrors.username)}
              />
            </InputWrapper>
          </Field>

          <Field label="Email" htmlFor="email" error={touched.email && fieldErrors.email}>
            <InputWrapper icon={<Mail size={15} />}>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
                {...blurProps}
                placeholder="your@email.com"
                className={inputClass(touched.email && fieldErrors.email)}
              />
            </InputWrapper>
          </Field>
        </div>

        {/* Row: Mobile + Role */}
        <div className="reg-form__row">
          <Field label="Mobile Number" htmlFor="mobile_number" optional
            error={touched.mobile_number && fieldErrors.mobile_number}>
            <InputWrapper icon={<Phone size={15} />}>
              <input
                id="mobile_number"
                name="mobile_number"
                type="tel"
                autoComplete="tel"
                value={formData.mobile_number}
                onChange={handleChange}
                {...blurProps}
                placeholder="10-digit number"
                className={inputClass(touched.mobile_number && fieldErrors.mobile_number)}
              />
            </InputWrapper>
          </Field>

          <Field label="Role" htmlFor="role">
            <InputWrapper icon={<Shield size={15} />}>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleRoleChange}
                className="reg-form__input reg-form__select"
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </InputWrapper>
          </Field>
        </div>

        {/* Registration code — conditional */}
        {requiresCode && (
          <Field label="Registration Code" htmlFor="reg_code"
            error={touched.reg_code && fieldErrors.reg_code}>
            <InputWrapper icon={<KeyRound size={15} />}>
              <input
                id="reg_code"
                name="reg_code"
                type="text"
                value={formData.reg_code}
                onChange={handleChange}
                {...blurProps}
                placeholder={`Enter ${formData.role} registration code`}
                className={inputClass(touched.reg_code && fieldErrors.reg_code)}
              />
            </InputWrapper>
          </Field>
        )}

        {/* Row: Password + Confirm */}
        <div className="reg-form__row">
          <Field label="Password" htmlFor="password"
            error={touched.password && fieldErrors.password}>
            <InputWrapper icon={<Lock size={15} />}>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                {...blurProps}
                placeholder="Min. 8 characters"
                className={inputClass(touched.password && fieldErrors.password, true)}
              />
              <EyeToggle show={showPassword} onToggle={() => setShowPassword((v) => !v)} />
            </InputWrapper>
          </Field>

          <Field label="Confirm Password" htmlFor="confirm_password"
            error={touched.confirm_password && fieldErrors.confirm_password}>
            <InputWrapper icon={<Lock size={15} />}>
              <input
                id="confirm_password"
                name="confirm_password"
                type={showConfirm ? 'text' : 'password'}
                autoComplete="new-password"
                value={formData.confirm_password}
                onChange={handleChange}
                {...blurProps}
                placeholder="Repeat password"
                className={inputClass(touched.confirm_password && fieldErrors.confirm_password, true)}
              />
              <EyeToggle show={showConfirm} onToggle={() => setShowConfirm((v) => !v)} />
            </InputWrapper>
          </Field>
        </div>

        <button type="submit" disabled={isLoading} className="reg-form__btn-primary">
          {isLoading ? 'Registering…' : 'Register Account'}
        </button>

        <button type="button" onClick={onNavigateToLogin} className="reg-form__btn-secondary">
          Back to Login
        </button>

      </form>

      <p className="reg-form__footer-note">
        Unauthorised access is a criminal offence under the IT Act, 2000.
      </p>
    </div>
  );
}

/* Returns input className, adding error modifier when there's an active error */
function inputClass(hasError, isPassword = false) {
  let cls = 'reg-form__input';
  if (isPassword) cls += ' reg-form__input--password';
  if (hasError)   cls += ' reg-form__input--error';
  return cls;
}

/* ── Helper components ───────────────────────────────────────────────────── */

function Field({ label, htmlFor, optional, error, children }) {
  return (
    <div className="reg-form__field">
      <label htmlFor={htmlFor} className="reg-form__label">
        {label}
        {optional && <span className="reg-form__label-optional"> (optional)</span>}
      </label>
      {children}
      {/* Reserve no space when no error — just render when needed */}
      {error && <p className="reg-form__field-error">{error}</p>}
    </div>
  );
}

function InputWrapper({ icon, children }) {
  return (
    <div className="reg-form__input-wrapper">
      <span className="reg-form__input-icon">{icon}</span>
      {children}
    </div>
  );
}

function EyeToggle({ show, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="reg-form__eye-btn"
      aria-label={show ? 'Hide password' : 'Show password'}
    >
      {show ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  );
}
