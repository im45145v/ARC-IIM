"""
Database migration utilities for schema updates.

This module provides functions to safely migrate existing databases
to new schema versions without losing data.
"""

from sqlalchemy import inspect, text

from .connection import engine
from .models import AccountUsage, Base, ScrapingQueue


def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_add_account_usage_table() -> None:
    """
    Add the account_usage table if it doesn't exist.
    
    This migration adds support for tracking LinkedIn account usage
    for rate limiting purposes.
    """
    if not check_table_exists("account_usage"):
        AccountUsage.__table__.create(bind=engine)
        print("✓ Created account_usage table")
    else:
        print("✓ account_usage table already exists")


def migrate_add_scraping_queue_table() -> None:
    """
    Add the scraping_queue table if it doesn't exist.
    
    This migration adds support for queue-based scraping management.
    """
    if not check_table_exists("scraping_queue"):
        ScrapingQueue.__table__.create(bind=engine)
        print("✓ Created scraping_queue table")
    else:
        print("✓ scraping_queue table already exists")


def migrate_add_account_email_to_scraping_logs() -> None:
    """
    Add account_email column to scraping_logs if it doesn't exist.
    
    This migration adds tracking of which account was used for each scrape.
    """
    inspector = inspect(engine)
    
    if not check_table_exists("scraping_logs"):
        print("✓ scraping_logs table doesn't exist yet, will be created by init_database()")
        return
    
    columns = [col['name'] for col in inspector.get_columns("scraping_logs")]
    
    if "account_email" not in columns:
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE scraping_logs ADD COLUMN account_email VARCHAR(255)"
            ))
            conn.commit()
        print("✓ Added account_email column to scraping_logs")
    else:
        print("✓ account_email column already exists in scraping_logs")


def migrate_add_performance_indexes() -> None:
    """
    Add performance optimization indexes if they don't exist.
    
    This migration adds composite and specialized indexes for better query performance.
    """
    with engine.connect() as conn:
        # Index for scraping_queue status and priority
        conn.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_scraping_queue_status_priority 
            ON scraping_queue(status, priority DESC)
            """
        ))
        
        # Index for scraping_logs created_at for audit queries
        conn.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_scraping_logs_created_at 
            ON scraping_logs(created_at DESC)
            """
        ))
        
        # Index for scraping_logs account_email
        conn.execute(text(
            """
            CREATE INDEX IF NOT EXISTS idx_scraping_logs_account_email 
            ON scraping_logs(account_email)
            """
        ))
        
        conn.commit()
    
    print("✓ Created performance indexes")


def run_all_migrations() -> None:
    """
    Run all database migrations in order.
    
    This function should be called after init_database() to ensure
    all schema updates are applied to existing databases.
    """
    print("Running database migrations...")
    
    migrate_add_account_usage_table()
    migrate_add_scraping_queue_table()
    migrate_add_account_email_to_scraping_logs()
    migrate_add_performance_indexes()
    
    print("✓ All migrations completed successfully")


def get_migration_status() -> dict[str, bool]:
    """
    Get the status of all migrations.
    
    Returns:
        Dictionary mapping migration names to completion status
    """
    return {
        "account_usage_table": check_table_exists("account_usage"),
        "scraping_queue_table": check_table_exists("scraping_queue"),
        "scraping_logs_table": check_table_exists("scraping_logs"),
    }
