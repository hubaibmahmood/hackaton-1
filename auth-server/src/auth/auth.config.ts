/**
 * better-auth configuration for authentication server.
 * Configures email/password authentication with JWT tokens.
 */
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { prisma } from '../database/client';
import { env } from '../config/env';

export const auth = betterAuth({
  // Database adapter using Prisma
  database: prismaAdapter(prisma, {
    provider: 'postgresql',
  }),

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: process.env.NODE_ENV === 'production',
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days (in seconds)
    updateAge: 60 * 60 * 24, // Refresh daily (in seconds)
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  // JWT configuration
  secret: env.jwtSecret,

  // Advanced session settings
  advanced: {
    crossSubDomainCookies: {
      enabled: false,
    },
    useSecureCookies: env.nodeEnv === 'production',
    cookiePrefix: 'better-auth',
  },

  // Rate limiting (handled by middleware, but configure here)
  rateLimit: {
    enabled: true,
    window: 60, // 1 minute window
    max: 10, // 10 requests per window
  },

  // Trusted origins for CORS
  trustedOrigins: env.corsOrigins,
});

export default auth;
