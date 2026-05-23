/**
 * api.js
 * ------
 * Thin fetch wrapper for the Crime Records Portal API.
 * Base URL: http://localhost:8000/api/v1
 *
 * All requests that need auth attach the JWT from localStorage automatically.
 * Throws an Error with a human-readable message on non-2xx responses.
 */

const BASE_URL = '/api/v1';

/**
 * Core fetch wrapper.
 * @param {string} path       - e.g. '/auth/login'
 * @param {RequestInit} opts  - standard fetch options
 * @param {boolean} withAuth  - attach Bearer token if true
 */
async function request(path, opts = {}, withAuth = false) {
  const headers = { 'Content-Type': 'application/json', ...opts.headers };

  if (withAuth) {
    const token = localStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...opts, headers });

  // Parse body regardless — error responses also carry JSON detail
  let body;
  try {
    body = await res.json();
  } catch {
    body = null;
  }

  if (!res.ok) {
    // FastAPI error shape: { detail: string | object }
    const detail = body?.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((e) => e.msg).join(', ')
        : `Request failed (${res.status})`;
    throw new Error(message);
  }

  return body;
}

// ---------------------------------------------------------------------------
// Auth endpoints
// ---------------------------------------------------------------------------

/**
 * POST /auth/login
 * @param {{ username: string, password: string }} credentials
 * @returns {Promise<{ access_token: string, token_type: string, expires_at: string }>}
 */
export function loginUser(credentials) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

/**
 * POST /auth/register
 * @param {{ username, email, mobile_number?, password, confirm_password }} payload
 * @returns {Promise<{ user_id, username, email, mobile_number, role, is_active }>}
 */
export function registerUser(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * POST /auth/change-password  (requires auth)
 * @param {{ username, current_password, new_password }} payload
 */
export function changePassword(payload) {
  return request('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  }, true);
}
