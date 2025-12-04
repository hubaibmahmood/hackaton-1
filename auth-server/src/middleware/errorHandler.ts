/**
 * Global error handler middleware for Express.
 * Catches all errors and returns consistent error responses.
 */
import { Request, Response, NextFunction } from 'express';
import { AppError, ValidationError } from '../utils/errors.js';
import { logger } from '../utils/logger.js';

/**
 * Error response interface
 */
interface ErrorResponse {
  error: string;
  message: string;
  errors?: Record<string, string[]>;
  stack?: string;
}

/**
 * Global error handler middleware.
 * Must be registered LAST in the middleware chain.
 */
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Default to 500 Internal Server Error
  let statusCode = 500;
  let message = 'Internal Server Error';
  let errors: Record<string, string[]> | undefined;

  // Handle AppError and its subclasses
  if (err instanceof AppError) {
    statusCode = err.statusCode;
    message = err.message;

    // Include validation errors if present
    if (err instanceof ValidationError && err.errors) {
      errors = err.errors;
    }

    // Log based on severity
    if (err.isOperational) {
      logger.warn('Operational error', {
        statusCode,
        message: err.message,
        path: req.path,
        method: req.method,
        ip: req.ip,
      });
    } else {
      logger.error('Non-operational error', {
        statusCode,
        message: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method,
      });
    }
  } else {
    // Unknown error type - log with full details
    logger.error('Unhandled error', {
      error: err.message,
      stack: err.stack,
      path: req.path,
      method: req.method,
    });
  }

  // Build error response
  const errorResponse: ErrorResponse = {
    error: statusCode >= 500 ? 'Internal Server Error' : message,
    message,
  };

  // Include validation errors if present
  if (errors) {
    errorResponse.errors = errors;
  }

  // Include stack trace in development
  if (process.env.NODE_ENV === 'development') {
    errorResponse.stack = err.stack;
  }

  // Send error response
  res.status(statusCode).json(errorResponse);
}

/**
 * Async error handler wrapper.
 * Wraps async route handlers to catch errors and pass to error middleware.
 */
export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
