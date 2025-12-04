/**
 * Environment variable validation utility.
 * Ensures all required environment variables are set on server startup.
 */

interface RequiredEnvVars {
  DATABASE_URL?: string;
  NEON_DB_URL?: string;
  JWT_SECRET: string;
  NODE_ENV?: string;
  PORT?: string;
  CORS_ORIGINS?: string;
}

interface ValidatedEnv {
  databaseUrl: string;
  jwtSecret: string;
  nodeEnv: string;
  port: number;
  corsOrigins: string[];
}

/**
 * Validate that all required environment variables are set.
 * Throws an error if any required variables are missing or invalid.
 *
 * @returns {ValidatedEnv} Validated and typed environment variables
 * @throws {Error} If required environment variables are missing
 */
export function validateEnv(): ValidatedEnv {
  const errors: string[] = [];

  // Check for database URL (either DATABASE_URL or NEON_DB_URL)
  const databaseUrl =
    process.env.DATABASE_URL || process.env.NEON_DB_URL;

  if (!databaseUrl) {
    errors.push('DATABASE_URL or NEON_DB_URL is required');
  } else if (
    !databaseUrl.startsWith('postgresql://') &&
    !databaseUrl.startsWith('postgres://')
  ) {
    errors.push('DATABASE_URL must be a valid PostgreSQL connection string');
  }

  // Check for JWT secret
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    errors.push('JWT_SECRET is required');
  } else if (jwtSecret.length < 32) {
    errors.push('JWT_SECRET must be at least 32 characters long');
  }

  // Validate NODE_ENV
  const nodeEnv = process.env.NODE_ENV || 'development';
  const validEnvs = ['development', 'production', 'test'];
  if (!validEnvs.includes(nodeEnv)) {
    errors.push(
      `NODE_ENV must be one of: ${validEnvs.join(', ')} (got: ${nodeEnv})`
    );
  }

  // Validate PORT
  const port = parseInt(process.env.PORT || '3000', 10);
  if (isNaN(port) || port < 1 || port > 65535) {
    errors.push('PORT must be a valid port number between 1 and 65535');
  }

  // Parse CORS origins
  const corsOrigins = process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(',').map((origin) => origin.trim())
    : ['http://localhost:3000'];

  // If there are errors, throw with all messages
  if (errors.length > 0) {
    const errorMessage = [
      '❌ Environment variable validation failed:',
      ...errors.map((err) => `  - ${err}`),
      '',
      'Please check your .env file and ensure all required variables are set.',
    ].join('\n');

    throw new Error(errorMessage);
  }

  // Return validated environment
  return {
    databaseUrl: databaseUrl!,
    jwtSecret: jwtSecret!,
    nodeEnv,
    port,
    corsOrigins,
  };
}

/**
 * Validate environment variables on module load.
 * This ensures that the server won't start with invalid configuration.
 */
let validatedEnv: ValidatedEnv;

try {
  validatedEnv = validateEnv();
  console.log('✅ Environment variables validated successfully');
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}

// Export validated environment for use throughout the application
export const env = validatedEnv;

export default env;
