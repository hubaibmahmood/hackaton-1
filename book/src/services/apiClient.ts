/**
 * Axios client for API Server communication.
 * Handles profile and personalization requests to the FastAPI backend.
 * Automatically includes JWT tokens from auth state.
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, setAccessToken } from './tokenStore';

// API Server base URL from environment or default
// Handle process.env safely for browser environment
const getEnvVar = (key: string, defaultValue: string): string => {
  try {
    return process.env[key] || defaultValue;
  } catch {
    return defaultValue;
  }
};

const API_SERVER_URL = getEnvVar('REACT_APP_API_SERVER_URL', 'http://localhost:8000');

/**
 * Create Axios instance for API Server
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_SERVER_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - Add JWT token and correlation ID
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get JWT token from in-memory store
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add correlation ID for request tracking
    const correlationId = crypto.randomUUID();
    config.headers['X-Correlation-ID'] = correlationId;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle errors consistently
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle common error responses
    if (error.response) {
      const status = error.response.status;
      const data: any = error.response.data;

      // Handle specific error cases
      switch (status) {
        case 401:
          console.error('Authentication required:', data.detail);
          // Clear invalid token
          setAccessToken(null);
          // Optionally redirect to login
          // window.location.href = '/signin';
          break;
        case 403:
          console.error('Access forbidden:', data.detail);
          break;
        case 404:
          console.error('Resource not found:', data.detail);
          break;
        case 429:
          console.error('Rate limit exceeded:', data.detail);
          break;
        case 500:
          console.error('Server error:', data.detail);
          break;
        default:
          console.error('Request failed:', data.detail || data.message);
      }
    } else if (error.request) {
      console.error('No response from API server');
    } else {
      console.error('Request setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
