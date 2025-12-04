/**
 * Structured logging utility with correlation IDs.
 * Provides consistent log format across the auth-server.
 */
import { randomUUID } from 'crypto';

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

interface LogContext {
  [key: string]: any;
  correlationId?: string;
  timestamp?: string;
}

class Logger {
  private context: LogContext = {};

  /**
   * Set global context that will be included in all logs
   */
  setContext(context: LogContext): void {
    this.context = { ...this.context, ...context };
  }

  /**
   * Clear global context
   */
  clearContext(): void {
    this.context = {};
  }

  /**
   * Generate a correlation ID for request tracking
   */
  generateCorrelationId(): string {
    return randomUUID();
  }

  /**
   * Format log entry with timestamp and correlation ID
   */
  private formatLog(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const correlationId = context?.correlationId || this.context.correlationId || 'no-correlation-id';

    const logEntry = {
      level,
      timestamp,
      correlationId,
      message,
      ...this.context,
      ...context,
    };

    return JSON.stringify(logEntry);
  }

  /**
   * Log debug message
   */
  debug(message: string, context?: LogContext): void {
    if (process.env.NODE_ENV === 'development') {
      console.log(this.formatLog(LogLevel.DEBUG, message, context));
    }
  }

  /**
   * Log info message
   */
  info(message: string, context?: LogContext): void {
    console.log(this.formatLog(LogLevel.INFO, message, context));
  }

  /**
   * Log warning message
   */
  warn(message: string, context?: LogContext): void {
    console.warn(this.formatLog(LogLevel.WARN, message, context));
  }

  /**
   * Log error message
   */
  error(message: string, context?: LogContext): void {
    console.error(this.formatLog(LogLevel.ERROR, message, context));
  }

  /**
   * Create a child logger with inherited context
   */
  child(context: LogContext): Logger {
    const childLogger = new Logger();
    childLogger.setContext({ ...this.context, ...context });
    return childLogger;
  }
}

// Export singleton instance
export const logger = new Logger();

// Export Logger class for testing
export { Logger };

export default logger;
