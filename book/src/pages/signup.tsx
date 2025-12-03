/**
 * Signup page with two-step registration flow.
 * Step 1: Email/password signup
 * Step 2: Background profile completion
 */
import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { SignupForm } from '../components/Auth/SignupForm';
import { ProfileForm, ProfileFormData } from '../components/Auth/ProfileForm';
import { useSignup } from '../hooks/useSignup';
import { useProfile } from '../hooks/useProfile';
import type { SignupResponse } from '../types/auth';
import styles from './signup.module.css';

type SignupStep = 'account' | 'profile' | 'complete';

export default function SignupPage() {
  const [step, setStep] = useState<SignupStep>('account');
  const [signupData, setSignupData] = useState<SignupResponse | null>(null);

  const { signup, loading: signupLoading, error: signupError } = useSignup();
  const profile = signupData ? useProfile(signupData.user.id) : null;

  const handleSignupSubmit = async (email: string, password: string) => {
    try {
      const response = await signup(email, password);
      setSignupData(response);
      setStep('profile');
    } catch (error) {
      // Error is handled by useSignup hook
      console.error('Signup failed:', error);
    }
  };

  const handleProfileSubmit = async (profileData: ProfileFormData) => {
    if (!profile) return;

    try {
      await profile.createProfile(profileData);
      setStep('complete');
    } catch (error) {
      // Error is handled by useProfile hook
      console.error('Profile creation failed:', error);
    }
  };

  const handleStartOver = () => {
    setStep('account');
    setSignupData(null);
    localStorage.removeItem('authToken');
  };

  return (
    <Layout
      title="Sign Up"
      description="Create your Physical AI textbook account with personalized learning"
    >
      <div className={styles.container}>
        <div className={styles.content}>
          {/* Progress indicator */}
          <div className={styles.progressBar}>
            <div
              className={`${styles.progressStep} ${
                step === 'account' ? styles.active : styles.completed
              }`}
            >
              1. Account
            </div>
            <div
              className={`${styles.progressStep} ${
                step === 'profile' ? styles.active : step === 'complete' ? styles.completed : ''
              }`}
            >
              2. Background
            </div>
            <div className={`${styles.progressStep} ${step === 'complete' ? styles.active : ''}`}>
              3. Complete
            </div>
          </div>

          {/* Step 1: Account creation */}
          {step === 'account' && (
            <div className={styles.stepContainer}>
              <div className={styles.header}>
                <h1 className={styles.title}>Create Your Account</h1>
                <p className={styles.subtitle}>
                  Get started with personalized robotics learning
                </p>
              </div>

              <SignupForm
                onSubmit={handleSignupSubmit}
                loading={signupLoading}
                error={signupError}
              />

              <div className={styles.footer}>
                <p className={styles.footerText}>
                  Already have an account?{' '}
                  <a href="/signin" className={styles.link}>
                    Sign in
                  </a>
                </p>
              </div>
            </div>
          )}

          {/* Step 2: Profile completion */}
          {step === 'profile' && signupData && (
            <div className={styles.stepContainer}>
              <div className={styles.header}>
                <h1 className={styles.title}>Tell Us About Your Background</h1>
                <p className={styles.subtitle}>
                  We'll personalize your learning experience based on your expertise
                </p>
              </div>

              <ProfileForm
                onSubmit={handleProfileSubmit}
                loading={profile?.loading}
                error={profile?.error}
              />

              <div className={styles.footer}>
                <p className={styles.footerText}>
                  Signed up as: <strong>{signupData.user.email}</strong>
                </p>
              </div>
            </div>
          )}

          {/* Step 3: Completion */}
          {step === 'complete' && signupData && (
            <div className={styles.stepContainer}>
              <div className={styles.successContainer}>
                <div className={styles.successIcon}>✓</div>
                <h1 className={styles.title}>Welcome to Physical AI!</h1>
                <p className={styles.subtitle}>
                  Your account has been created and your profile is set up.
                </p>

                <div className={styles.successDetails}>
                  <p>
                    <strong>Email:</strong> {signupData.user.email}
                  </p>
                  <p>
                    Your learning experience will be tailored to your background and expertise level.
                  </p>
                </div>

                <div className={styles.actions}>
                  <a href="/" className={styles.primaryButton}>
                    Start Learning
                  </a>
                  <a href="/profile" className={styles.secondaryButton}>
                    View Profile
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
