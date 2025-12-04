import React from 'react';
import Layout from '@theme/Layout';
import SigninForm from '../components/Auth/SigninForm';

export default function SigninPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <div className="min-h-[calc(100vh-var(--ifm-navbar-height))] flex items-center justify-center bg-gradient-to-br from-blue-50 to-white dark:from-slate-900 dark:to-slate-950 p-4">
        <SigninForm />
      </div>
    </Layout>
  );
}
