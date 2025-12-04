/**
 * Custom authentication routes.
 * Extends better-auth with additional endpoints.
 */
import { Router } from 'express';
import { auth } from './auth.config.js';
import { logger } from '../utils/logger.js';

const router = Router();

/**
 * GET /api/auth/me
 * Get current user information from session
 */
router.get('/me', async (req, res, next) => {
  try {
    logger.debug('Attempting to get session for /me endpoint', {
      cookieHeader: req.headers.cookie, // Log the raw cookie header
    });

    const session = await auth.api.getSession({ headers: req.headers });

    if (!session) {
      logger.warn('No active session found for /me endpoint', {
        cookieHeader: req.headers.cookie,
      });
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'No active session found',
      });
    }

    logger.debug('Session found for /me endpoint', {
      userId: session.user.id,
      sessionId: session.session.id,
    });

    res.json({
      userId: session.user.id,
      email: session.user.email,
      emailVerified: session.user.emailVerified,
      createdAt: session.user.createdAt,
      // session.session contains the session details
      sessionId: session.session.id,
    });
  } catch (error) {
    logger.error('Error fetching current user', { error });
    next(error);
  }
});

/**
 * POST /api/auth/verify-token
 * Verify if a JWT token is valid (used by other services)
 */
router.post('/verify-token', async (req, res, next) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Token is required',
      });
    }

    // Verify token using better-auth
    const session = await auth.api.getSession({
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    if (!session) {
      return res.status(401).json({
        error: 'Invalid Token',
        message: 'Token is invalid or expired',
      });
    }

    res.json({
      valid: true,
      userId: session.user.id,
      email: session.user.email,
    });
  } catch (error) {
    logger.error('Error verifying token', { error });
    res.status(401).json({
      error: 'Invalid Token',
      message: 'Token verification failed',
    });
  }
});

/**
 * POST /api/auth/signin
 * Sign in with email and password
 */
router.post('/signin', async (req, res, next) => {
  try {
    const { email, password, rememberMe } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Email and password are required',
      });
    }

    // Use better-auth to sign in
    // We use the raw API and handle the response headers
    const result = await auth.api.signInEmail({
      body: { email, password, rememberMe },
      asResponse: true, // Get the full response object to handle headers/cookies
    });

    // Forward headers (Set-Cookie) from better-auth response to Express response
    if (result.headers) {
      result.headers.forEach((value, key) => {
        res.setHeader(key, value);
      });
    }

    // Return the body
    const body = await result.json();
    res.status(result.status).json(body);
  } catch (error: any) {
    logger.error('Signin error', { error: error.message || error });
    // If better-auth throws, it might be an APIError
    if (error.status) {
        return res.status(error.status).json(error.body || { message: error.message });
    }
    next(error);
  }
});

/**
 * POST /api/auth/signout
 * Sign out current user
 */
router.post('/signout', async (req, res, next) => {
  try {
    // Use better-auth to sign out
    const result = await auth.api.signOut({
      headers: req.headers, // Pass headers to identify session
      asResponse: true,
    });

     // Forward headers (Set-Cookie to clear)
    if (result.headers) {
      result.headers.forEach((value, key) => {
        res.setHeader(key, value);
      });
    }

    const body = await result.json();
    res.status(result.status).json(body);
  } catch (error) {
    logger.error('Signout error', { error });
    next(error);
  }
});

/**
 * POST /api/auth/refresh
 * Refresh session/token
 */
router.post('/refresh', async (req, res, next) => {
    try {
        // Refresh session - typically getSession updates the session if needed?
        // Or uses listSessions / refreshSession? 
        // better-auth usually handles refresh automatically on getSession if updateAge passed.
        // But let's expose an endpoint if explicit refresh is needed.
        
        // Actually, 'better-auth' doesn't explicitly have 'refreshSession' exposed in the same way as signin.
        // But we can just call getSession and if it updates, it returns new cookies?
        // Or simply verify the session.
        
        const result = await auth.api.getSession({
            headers: req.headers,
            asResponse: true
        });
        
        if (result.headers) {
            result.headers.forEach((value, key) => {
                res.setHeader(key, value);
            });
        }
        
        const body = await result.json();
        res.status(result.status).json(body);
    } catch (error) {
        logger.error('Refresh error', { error });
        next(error);
    }
});

export default router;
