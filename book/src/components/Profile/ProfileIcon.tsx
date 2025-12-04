import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import Link from '@docusaurus/Link';
import { useHistory } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './ProfileIcon.module.css';

const ProfileIcon: React.FC = () => {
  const { user, signout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const history = useHistory();
  const introPath = useBaseUrl('/docs/part-01-physical-ai/intro');

  const handleSignout = async () => {
    await signout();
    setIsOpen(false);
    history.push(introPath);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (!user) {
    return null;
  }

  const getInitials = (email: string) => {
    return email.charAt(0).toUpperCase();
  };

  return (
    <div className={styles.container} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={styles.iconButton}
        title={user.email}
        aria-label="User menu"
        aria-expanded={isOpen}
      >
        {getInitials(user.email)}
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.userInfo} title={user.email}>
            {user.email}
          </div>
          <Link
            to="/profile"
            className={styles.menuItem}
            onClick={() => setIsOpen(false)}
          >
            Profile Settings
          </Link>
          <button
            onClick={handleSignout}
            className={`${styles.menuItem} ${styles.signOut}`}
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};

export default ProfileIcon;