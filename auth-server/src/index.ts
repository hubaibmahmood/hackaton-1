import app from './app';
import { env } from './config/env';
import { logger } from './utils/logger';

// Start server
const PORT = env.port;

app.listen(PORT, () => {
  logger.info(`Auth server listening on port ${PORT}`);
  logger.info(`Environment: ${env.nodeEnv}`);
  logger.info(`CORS origins: ${env.corsOrigins.join(', ')}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});