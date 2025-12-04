/**
 * Root theme wrapper for Docusaurus
 * This component wraps the entire application
 */
import React, { Suspense, useState, useEffect } from 'react';
import { AuthProvider } from '../components/Auth/AuthProvider';

// Lazy load ChatBot to optimize initial bundle size
const ChatBot = React.lazy(() => import('../components/ChatBot').then(module => ({ default: module.ChatBot })));

export default function Root({ children }: { children: React.ReactNode }) {
  // Delay loading slightly to prioritize main content
  const [shouldLoad, setShouldLoad] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShouldLoad(true), 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AuthProvider>
      {children}
      {shouldLoad && (
        <Suspense fallback={null}>
          <ChatBot />
        </Suspense>
      )}
    </AuthProvider>
  );
}