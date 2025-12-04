/**
 * Validation utilities for authentication.
 * Provides additional validation beyond better-auth defaults.
 */

export interface PasswordValidationResult {
  valid: boolean;
  errors: string[];
}

export interface EmailValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validate password strength requirements.
 * Requirements:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one number
 * - Maximum 128 characters
 */
export function validatePassword(password: string): PasswordValidationResult {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  if (password.length > 128) {
    errors.push('Password must not exceed 128 characters');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate email format.
 * Uses RFC 5322 compliant regex.
 */
export function validateEmail(email: string): EmailValidationResult {
  if (!email || email.trim().length === 0) {
    return {
      valid: false,
      error: 'Email is required',
    };
  }

  // RFC 5322 compliant email regex (simplified)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return {
      valid: false,
      error: 'Invalid email format',
    };
  }

  // Additional checks
  if (email.length > 255) {
    return {
      valid: false,
      error: 'Email must not exceed 255 characters',
    };
  }

  return { valid: true };
}

/**
 * Validate signup data before sending to better-auth.
 * Returns array of validation errors.
 */
export function validateSignupData(
  email: string,
  password: string
): string[] {
  const errors: string[] = [];

  const emailValidation = validateEmail(email);
  if (!emailValidation.valid && emailValidation.error) {
    errors.push(emailValidation.error);
  }

  const passwordValidation = validatePassword(password);
  if (!passwordValidation.valid) {
    errors.push(...passwordValidation.errors);
  }

  return errors;
}
