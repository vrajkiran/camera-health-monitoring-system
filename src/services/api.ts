// Central API client service with automatic auth header injection and 401 session expiration handling

const TOKEN_KEY = 'surveillance_auth_token';
const USER_KEY = 'surveillance_auth_user';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string, remember: boolean = true): void {
  if (remember) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    sessionStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearStoredAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearStoredAuth();
    window.dispatchEvent(new CustomEvent('session-expired'));
    const errorData = await response.json().catch(() => ({ error: 'Session expired' }));
    throw new Error(errorData.error || 'Authentication required or session expired.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}: ${response.statusText}` }));
    throw new Error(errorData.error || errorData.message || `Request failed with status ${response.status}`);
  }

  return response.json();
}
