/**
 * In-memory token store for managing access tokens securely.
 * Tokens are not persisted to localStorage/sessionStorage to prevent XSS attacks.
 */

let accessToken: string | null = null;

export const getAccessToken = (): string | null => {
  return accessToken;
};

export const setAccessToken = (token: string | null): void => {
  accessToken = token;
};
