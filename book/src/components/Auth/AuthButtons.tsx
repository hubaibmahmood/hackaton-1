import React from 'react';
import Link from '@docusaurus/Link';
import { useAuth } from '../../hooks/useAuth';
import clsx from 'clsx'; // For conditional classnames

const AuthButtons: React.FC = () => {
  const { user, isLoading } = useAuth();

  // Don't render anything if loading or user is logged in
  if (isLoading || user) {
    return null;
  }

  return (
    <div className="flex items-center mr-2">
      <Link
        className={clsx(
          'button button--primary button--sm',
          'navbar-button--no-text'
        )}
        to="/signin"
      >
        Sign In / Sign Up
      </Link>
    </div>
  );
};

export default AuthButtons;