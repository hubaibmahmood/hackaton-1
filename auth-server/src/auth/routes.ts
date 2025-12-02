/**
 * Custom authentication routes.
 * Extends better-auth with additional endpoints.
 */
import { Router } from 'express';
import { auth } from './auth.config';
import { logger } from '../utils/logger';

const router = Router();

/**
 * GET /api/auth/me
 * Get current user information from session
 */
router.get('/me', async (req, res, next) => {
  try {
    const session = await auth.api.getSession({ headers: req.headers });

    if (!session) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'No active session found',
      });
    }

    res.json({
      userId: session.user.id,
      email: session.user.email,
      emailVerified: session.user.emailVerified,
      createdAt: session.user.createdAt,
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

export default router;
