import React from 'react';
import Layout from '@theme/Layout';
import ProtectedRoute from '../components/Auth/ProtectedRoute';
import { ProfileSettings } from '../components/Profile/ProfileSettings';

export default function ProfilePage(): JSX.Element {
  return (
    <Layout title="Profile Settings" description="Manage your profile and personalization settings">
      <ProtectedRoute>
        <ProfileSettings />
      </ProtectedRoute>
    </Layout>
  );
}
