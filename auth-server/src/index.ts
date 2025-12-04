import app from './app.js';
import { env } from './config/env.js';
import { logger } from './utils/logger.js';

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