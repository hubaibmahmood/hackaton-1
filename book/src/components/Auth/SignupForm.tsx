/**
 * Signup form component.
 * Handles email and password input with validation.
 */
import React, { useState } from 'react';
import { Button } from '../common/Button';
import { ErrorMessage } from '../common/ErrorMessage';
import styles from './SignupForm.module.css';

interface SignupFormProps {
  onSubmit: (email: string, password: string) => void;
  loading?: boolean;
  error?: string | null;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSubmit, loading, error }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateEmail = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Email is required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Invalid email format';
    }
    return undefined;
  };

  const validatePassword = (value: string): string | undefined => {
    if (!value) {
      return 'Password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!/[A-Z]/.test(value)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(value)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/[0-9]/.test(value)) {
      return 'Password must contain at least one number';
    }
    return undefined;
  };

  const validateConfirmPassword = (value: string): string | undefined => {
    if (!value) {
      return 'Please confirm your password';
    }
    if (value !== password) {
      return 'Passwords do not match';
    }
    return undefined;
  };

  const handleBlur = (field: string) => {
    setTouched({ ...touched, [field]: true });

    const newErrors: FormErrors = { ...errors };

    if (field === 'email') {
      newErrors.email = validateEmail(email);
    } else if (field === 'password') {
      newErrors.password = validatePassword(password);
      // Re-validate confirm password if it's been touched
      if (touched.confirmPassword) {
        newErrors.confirmPassword = validateConfirmPassword(confirmPassword);
      }
    } else if (field === 'confirmPassword') {
      newErrors.confirmPassword = validateConfirmPassword(confirmPassword);
    }

    setErrors(newErrors);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const newErrors: FormErrors = {
      email: validateEmail(email),
      password: validatePassword(password),
      confirmPassword: validateConfirmPassword(confirmPassword),
    };

    setErrors(newErrors);
    setTouched({ email: true, password: true, confirmPassword: true });

    // Check if there are any errors
    const hasErrors = Object.values(newErrors).some((error) => error !== undefined);

    if (!hasErrors) {
      onSubmit(email, password);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.signupForm}>
      <div className={styles.formGroup}>
        <label htmlFor="email" className={styles.label}>
          Email Address *
        </label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => handleBlur('email')}
          className={`${styles.input} ${touched.email && errors.email ? styles.inputError : ''}`}
          placeholder="you@example.com"
          disabled={loading}
          autoComplete="email"
        />
        {touched.email && errors.email && (
          <span className={styles.fieldError}>{errors.email}</span>
        )}
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="password" className={styles.label}>
          Password *
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => handleBlur('password')}
          className={`${styles.input} ${touched.password && errors.password ? styles.inputError : ''}`}
          placeholder="Minimum 8 characters"
          disabled={loading}
          autoComplete="new-password"
        />
        {touched.password && errors.password && (
          <span className={styles.fieldError}>{errors.password}</span>
        )}
        {!errors.password && touched.password && (
          <span className={styles.hint}>
            Must include uppercase, lowercase, and number
          </span>
        )}
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="confirmPassword" className={styles.label}>
          Confirm Password *
        </label>
        <input
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          onBlur={() => handleBlur('confirmPassword')}
          className={`${styles.input} ${touched.confirmPassword && errors.confirmPassword ? styles.inputError : ''}`}
          placeholder="Re-enter your password"
          disabled={loading}
          autoComplete="new-password"
        />
        {touched.confirmPassword && errors.confirmPassword && (
          <span className={styles.fieldError}>{errors.confirmPassword}</span>
        )}
      </div>

      {error && <ErrorMessage message={error} />}

      <Button
        type="submit"
        variant="primary"
        fullWidth
        disabled={loading}
        isLoading={loading}
        loadingText="Creating Account..."
      >
        Create Account
      </Button>
    </form>
  );
};
