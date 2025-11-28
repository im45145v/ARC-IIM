-- Alumni Management System - Database Initialization Script
-- =========================================================
-- This script runs automatically when the Docker container starts for the first time.
-- It creates the necessary extensions and sets up the database for the Alumni system.

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create indexes for better search performance (after tables are created by SQLAlchemy)
-- Note: These are created here as a reference. The actual tables are created by SQLAlchemy's init_database()

-- Additional indexes for performance optimization (created after tables exist)
-- These will be created by a migration script if tables already exist

-- Composite index for account_usage to enforce uniqueness and improve lookups
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_account_usage_email_date ON account_usage(account_email, date);

-- Index for scraping_queue to optimize queue processing
-- CREATE INDEX IF NOT EXISTS idx_scraping_queue_status_priority ON scraping_queue(status, priority DESC);

-- Index for scraping_logs to optimize audit queries
-- CREATE INDEX IF NOT EXISTS idx_scraping_logs_created_at ON scraping_logs(created_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_scraping_logs_account_email ON scraping_logs(account_email);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE alumni_db TO postgres;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Alumni database initialized successfully!';
END $$;
