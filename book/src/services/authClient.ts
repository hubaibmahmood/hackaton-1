/**
 * Axios client for Auth Server communication.
 * Handles authentication requests to the Node.js auth-server.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// Auth Server base URL from environment or default
// Handle process.env safely for browser environment
const getEnvVar = (key: string, defaultValue: string): string => {
  try {
    return process.env[key] || defaultValue;
  } catch {
    return defaultValue;
  }
};

// const AUTH_SERVER_URL = getEnvVar('DOCUSAURUS_AUTH_SERVER_URL', 'http://localhost:3001');
const AUTH_SERVER_URL = getEnvVar(
  'DOCUSAURUS_AUTH_SERVER_URL',
  'https://hackaton-1-three.vercel.app/',
);

/**
 * Create Axios instance for Auth Server
 */
export const authClient: AxiosInstance = axios.create({
  baseURL: AUTH_SERVER_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Send cookies for session management
});

/**
 * Request interceptor - Add correlation ID
 */
authClient.interceptors.request.use(
  (config) => {
    // Add correlation ID for request tracking
    const correlationId = crypto.randomUUID();
    config.headers['X-Correlation-ID'] = correlationId;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

/**
 * Response interceptor - Handle errors consistently
 */
authClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle common error responses
    if (error.response) {
      const status = error.response.status;
      const data: any = error.response.data;

      // Customize error message based on status code
      switch (status) {
        case 401:
          console.error('Authentication failed:', data.message);
          break;
        case 403:
          console.error('Access forbidden:', data.message);
          break;
        case 429:
          console.error('Rate limit exceeded:', data.message);
          break;
        case 500:
          console.error('Server error:', data.message);
          break;
        default:
          console.error('Request failed:', data.message);
      }
    } else if (error.request) {
      console.error('No response from auth server');
    } else {
      console.error('Request setup error:', error.message);
    }

    return Promise.reject(error);
  },
);

export default authClient;
