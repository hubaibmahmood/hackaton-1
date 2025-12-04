/**
 * better-auth configuration for authentication server.
 * Configures email/password authentication with JWT tokens.
 */
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { prisma } from '../database/client.js';
import { env } from '../config/env.js';
import { customSession } from 'better-auth/plugins'; // Import customSession

export const auth = betterAuth({
  // Database adapter using Prisma
  database: prismaAdapter(prisma, {
    provider: 'postgresql',
  }),

  plugins: [
    // customSession({ // Temporarily disable customSession plugin
    //   async onSessionCreate(session, context) {
    //     let ipAddress = context.request.headers.get("x-forwarded-for") || context.request.ip;
    //     if (ipAddress === "") {
    //       ipAddress = null;
    //     }

    //     let userAgent = context.request.headers.get("user-agent");
    //     if (userAgent === "") {
    //       userAgent = null;
    //     }

    //     return {
    //       ...session,
    //       ipAddress,
    //       userAgent,
    //     };
    //   },
    //   async onSessionGet(session, context) { // Re-added onSessionGet after checking docs
    //     return session;
    //   },
    // }),
  ],

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Temporarily disabled by user request
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Session configuration
  session: {
    modelName: 'userSession',
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
    defaultCookieAttributes: {
        httpOnly: true,
        secure: env.nodeEnv === 'production',
        sameSite: env.nodeEnv === 'production' ? 'none' : 'lax', // 'none' for cross-site requests in production
        path: '/',
    },
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
