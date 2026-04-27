/**
 * API base with no trailing slash.
 * - If `VITE_API_URL` is set → use it (custom / production backend).
 * - If unset in Vite dev → '' so `/api/...` hits the dev-server proxy (avoids wrong host + CORS).
 * - If unset in production → same browser origin (typical reverse-proxy setup).
 */
export function getApiBaseUrl(): string {
    const env = import.meta.env.VITE_API_URL;
    if (typeof env === 'string' && env.trim() !== '') {
        return env.trim().replace(/\/+$/, '');
    }
    if (import.meta.env.DEV) {
        return '';
    }
    if (typeof window !== 'undefined' && window.location?.origin) {
        return window.location.origin;
    }
    return 'http://localhost:10000';
}

const BASE_URL = getApiBaseUrl();

export function getToken(): string | null {
    return localStorage.getItem('auth_token');
}

export function setToken(token: string) {
    localStorage.setItem('auth_token', token);
}

export function removeToken() {
    localStorage.removeItem('auth_token');
}

export function isAuthenticated(): boolean {
    return !!getToken();
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = getToken();
    const headers = new Headers(options.headers || {});

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    // Only set JSON Content-Type when there is a body (GET must not send application/json).
    const body = options.body;
    if (!headers.has('Content-Type') && body != null && !(body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const response = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        removeToken();
        if (window.location.pathname !== '/auth') {
            window.location.href = '/auth';
        }
    }

    return response;
}

export function getAuthHeaders(): Record<string, string> {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}
