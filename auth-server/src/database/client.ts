/**
 * Prisma database client configuration for auth-server.
 * Connects to shared Neon PostgreSQL database with connection pooling.
 */
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';

// Singleton pattern for Prisma Client
declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Database connection string from environment variables
const connectionString = process.env.DATABASE_URL || process.env.NEON_DB_URL;

if (!connectionString) {
  throw new Error(
    'DATABASE_URL or NEON_DB_URL must be set in environment variables'
  );
}

const adapter = new PrismaPg({ connectionString });

export const prisma =
  global.prisma ||
  new PrismaClient({
    adapter,
    log:
      process.env.NODE_ENV === 'development'
        ? ['query', 'error', 'warn']
        : ['error'],
    // Connection pool configuration for Neon Serverless
    // Neon uses connection pooling by default, but we configure it explicitly
  });

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

// Graceful shutdown
process.on('beforeExit', async () => {
  await prisma.$disconnect();
});

export default prisma;
