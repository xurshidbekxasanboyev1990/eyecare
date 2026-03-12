/**
 * EyeCare API Service
 * Backend API bilan ishlash uchun service
 */

// API Base URL - production/development muhitga qarab o'zgaradi
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://104.104.104.10:8000/api/v1';

// Token storage
const TOKEN_KEY = 'eyecare_token';
const REFRESH_TOKEN_KEY = 'eyecare_refresh_token';

/**
 * Get stored access token
 */
export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Set access token
 */
export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get refresh token
 */
export function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Set refresh token
 */
export function setRefreshToken(token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

/**
 * Clear tokens (logout)
 */
export function clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
    return !!getToken();
}

/**
 * API request helper
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add auth token if available
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle 401 - try refresh token
        if (response.status === 401 && getRefreshToken()) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Retry original request
                headers['Authorization'] = `Bearer ${getToken()}`;
                const retryResponse = await fetch(url, { ...options, headers });
                return handleResponse(retryResponse);
            }
        }

        return handleResponse(response);
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Handle API response
 */
async function handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        const error = new Error(data.message || 'Xatolik yuz berdi');
        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}

/**
 * Refresh access token
 */
async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                refresh_token: getRefreshToken()
            })
        });

        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            if (data.refresh_token) {
                setRefreshToken(data.refresh_token);
            }
            return true;
        }

        // Refresh failed - clear tokens
        clearTokens();
        return false;
    } catch (error) {
        clearTokens();
        return false;
    }
}

// ==================== AUTH API ====================

/**
 * Register new user
 */
export async function register(userData) {
    const response = await apiRequest('/mobile/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    });

    if (response.access_token) {
        setToken(response.access_token);
        setRefreshToken(response.refresh_token);
    }

    return response;
}

/**
 * Login user
 */
export async function login(phone, password) {
    const response = await apiRequest('/mobile/auth/login', {
        method: 'POST',
        body: JSON.stringify({ phone, password })
    });

    if (response.access_token) {
        setToken(response.access_token);
        setRefreshToken(response.refresh_token);
    }

    return response;
}

/**
 * Logout user
 */
export function logout() {
    clearTokens();
}

// ==================== USER API ====================

/**
 * Get user profile
 */
export async function getProfile() {
    return apiRequest('/mobile/user/profile');
}

/**
 * Update user profile
 */
export async function updateProfile(data) {
    return apiRequest('/mobile/user/profile', {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// ==================== TESTS API ====================

/**
 * Get available test types
 */
export async function getTestTypes() {
    return apiRequest('/mobile/tests/types');
}

/**
 * Start a new test session
 */
export async function startTestSession(testType, deviceInfo = {}) {
    return apiRequest('/mobile/tests/start', {
        method: 'POST',
        body: JSON.stringify({
            test_type: testType,
            device_info: navigator.userAgent,
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            ...deviceInfo
        })
    });
}

/**
 * Submit test result
 */
export async function submitTestResult(sessionId, testType, resultData) {
    return apiRequest('/mobile/tests/submit', {
        method: 'POST',
        body: JSON.stringify({
            session_id: sessionId,
            test_type: testType,
            ...resultData
        })
    });
}

/**
 * Get test history
 */
export async function getTestHistory(page = 1, limit = 20) {
    return apiRequest(`/mobile/tests/history?page=${page}&limit=${limit}`);
}

/**
 * Get single test result
 */
export async function getTestResult(testId) {
    return apiRequest(`/mobile/tests/session/${testId}`);
}

// ==================== DOCTORS API ====================

/**
 * Get doctors list
 */
export async function getDoctors(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/mobile/doctors${queryString ? '?' + queryString : ''}`);
}

/**
 * Get doctor details
 */
export async function getDoctor(doctorId) {
    return apiRequest(`/mobile/doctors/${doctorId}`);
}

/**
 * Book appointment
 */
export async function bookAppointment(doctorId, date, time, reason) {
    return apiRequest(`/mobile/doctors/${doctorId}/appointment`, {
        method: 'POST',
        body: JSON.stringify({
            date,
            time,
            reason
        })
    });
}

/**
 * Get user appointments
 */
export async function getAppointments() {
    return apiRequest('/mobile/appointments');
}

// ==================== NOTIFICATIONS API ====================

/**
 * Get notifications
 */
export async function getNotifications() {
    return apiRequest('/mobile/notifications');
}

/**
 * Mark notification as read
 */
export async function markNotificationRead(notificationId) {
    return apiRequest(`/mobile/notifications/${notificationId}/read`, {
        method: 'POST'
    });
}

// Export API base URL for reference
export { API_BASE_URL };
