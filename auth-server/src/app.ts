import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { toNodeHandler } from 'better-auth/node';
import { env } from './config/env';
import { auth } from './auth/auth.config';
import authRoutes from './auth/routes';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';

const app = express();

// Security middleware
app.use(helmet());

// Enable trust proxy to correctly get client IP address
app.set('trust proxy', true);

// CORS configuration
app.use(
  cors({
    origin: env.corsOrigins,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Correlation-ID'],
  })
);

// Body parsing middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  logger.debug(`Incoming request: ${req.method} ${req.path}`, {
    ip: req.ip,
    ips: req.ips, // Log req.ips as well, which is an array of IPs from X-Forwarded-For
    userAgent: req.get('user-agent'),
  });
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('user-agent'),
  });
  next();
});

// Custom auth routes
app.use('/api/auth', authRoutes);

// Mount better-auth routes (handles /api/auth/signup, /api/auth/signin, etc.)
app.all('/api/auth/*', toNodeHandler(auth));

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Auth Server is running',
    status: 'online',
    docs: '/api/auth/docs' // Optional: link to docs if you have them
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'auth-server',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`,
  });
});

// Global error handler (must be last)
app.use(errorHandler);

export default app;
