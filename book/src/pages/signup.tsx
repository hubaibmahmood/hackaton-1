/**
 * Signup page with two-step registration flow.
 * Step 1: Email/password signup
 * Step 2: Background profile completion
 */
import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { SignupForm } from '../components/Auth/SignupForm';
import { ProfileForm, ProfileFormData } from '../components/Auth/ProfileForm';
import { useSignup } from '../hooks/useSignup';
import { useProfile } from '../hooks/useProfile';
import { useAuth } from '../hooks/useAuth';
import type { SignupResponse } from '../types/auth';
import useBaseUrl from '@docusaurus/useBaseUrl';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle2 } from 'lucide-react';

type SignupStep = 'account' | 'profile' | 'complete';

export default function SignupPage() {
  const [step, setStep] = useState<SignupStep>('account');
  const [signupData, setSignupData] = useState<SignupResponse | null>(null);
  const homePageUrl = useBaseUrl('/');

  const { signup, loading: signupLoading, error: signupError } = useSignup();
  const profile = useProfile();
  const { checkSession } = useAuth(); 
  const [creatingProfile, setCreatingProfile] = useState(false);

  const handleSignupSubmit = async (email: string, password: string) => {
    try {
      const response = await signup(email, password);
      setSignupData(response);
      // Sync auth state immediately after signup since useSignup sets the token
      await checkSession(); 
      setStep('profile');
    } catch (error) {
      // Error is handled by useSignup hook
      console.error('Signup failed:', error);
    }
  };

  const handleProfileSubmit = async (profileData: ProfileFormData) => {
    if (!signupData?.user?.id) {
      console.error('Missing user ID for profile creation');
      return;
    }

    setCreatingProfile(true);
    try {
      // Include user_id in the payload as required by the backend
      await profile.createProfile({
        ...profileData,
        user_id: signupData.user.id
      });
      setStep('complete');
      // Ensure session is fresh
      await checkSession();
    } catch (error) {
      // Error is handled by useProfile hook
      console.error('Profile creation failed:', error);
    } finally {
      setCreatingProfile(false);
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
      <div className="min-h-[calc(100vh-var(--ifm-navbar-height))] flex flex-col items-center py-12 px-4 bg-gradient-to-br from-blue-50 to-white dark:from-slate-900 dark:to-slate-950">
        <div className="w-full max-w-3xl">
          {/* Progress indicator */}
          <div className="flex justify-between mb-8 relative">
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-800 -z-10 -translate-y-1/2" />
            {[
              { id: 'account', label: '1. Account' },
              { id: 'profile', label: '2. Background' },
              { id: 'complete', label: '3. Complete' },
            ].map((s, index) => {
              const isActive = step === s.id;
              const isCompleted =
                (step === 'profile' && index === 0) ||
                (step === 'complete' && index <= 1);
              
              return (
                <div
                  key={s.id}
                  className={`px-6 py-2 rounded-full text-sm font-semibold transition-all border-2 ${
                    isActive
                      ? 'bg-primary text-primary-foreground border-primary shadow-lg scale-105'
                      : isCompleted
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-background text-muted-foreground border-gray-200 dark:border-gray-800'
                  }`}
                >
                  {s.label}
                </div>
              );
            })}
          </div>

          {/* Step 1: Account creation */}
          {step === 'account' && (
            <Card>
              <CardHeader className="text-center space-y-2">
                <CardTitle className="text-3xl font-bold">Create Your Account</CardTitle>
                <CardDescription className="text-lg">
                  Get started with personalized robotics learning
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SignupForm
                  onSubmit={handleSignupSubmit}
                  loading={signupLoading}
                  error={signupError}
                />
              </CardContent>
              <CardFooter className="justify-center">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{' '}
                  <Link to="/signin" className="text-primary font-medium hover:underline">
                    Sign in
                  </Link>
                </p>
              </CardFooter>
            </Card>
          )}

          {/* Step 2: Profile completion */}
          {step === 'profile' && signupData && (
            <Card>
              <CardHeader className="text-center space-y-2">
                <CardTitle className="text-3xl font-bold">Tell Us About Your Background</CardTitle>
                <CardDescription className="text-lg">
                  We&apos;ll personalize your learning experience based on your expertise
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ProfileForm
                  onSubmit={handleProfileSubmit}
                  loading={creatingProfile}
                  error={profile?.error}
                />
              </CardContent>
              <CardFooter className="justify-center">
                <p className="text-sm text-muted-foreground">
                  Signed up as: <strong>{signupData.user.email}</strong>
                </p>
              </CardFooter>
            </Card>
          )}

          {/* Step 3: Completion */}
          {step === 'complete' && signupData && (
            <Card className="text-center">
              <CardContent className="pt-12 pb-8 space-y-6">
                <div className="flex justify-center">
                  <div className="h-24 w-24 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                    <CheckCircle2 className="h-12 w-12 text-green-600 dark:text-green-400" />
                  </div>
                </div>
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold">Welcome to Physical AI!</h1>
                  <p className="text-lg text-muted-foreground">
                    Your account has been created and your profile is set up.
                  </p>
                </div>

                <div className="bg-muted/50 p-6 rounded-lg max-w-md mx-auto text-left space-y-2">
                  <p className="text-sm text-muted-foreground">Account Details:</p>
                  <p className="font-medium">{signupData.user.email}</p>
                  <p className="text-sm text-muted-foreground mt-4">
                    Your learning experience will be tailored to your background
                    and expertise level.
                  </p>
                </div>

                <div className="flex justify-center gap-4 pt-4">
                  <Button asChild size="lg">
                    <Link to={homePageUrl}>Start Learning</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg">
                    <Link to="/profile">View Profile</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}
