import React from 'react';
import Layout from '@theme/Layout';

export default function NotFound() {
  return (
    <Layout title="Page Not Found">
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '50vh',
          flexDirection: 'column',
        }}>
        <h1>404 - Page Not Found</h1>
        <p>We could not find what you were looking for.</p>
      </div>
    </Layout>
  );
}
