import React from 'react';
import { Redirect, useLocation } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';
import LoadingSpinner from '../common/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    // Redirect to signin, saving the current location to redirect back after login
    return <Redirect to={`/signin?from=${encodeURIComponent(location.pathname)}`} />;
  }

  return <>{children}</>;
}
