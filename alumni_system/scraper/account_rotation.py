"""
Account rotation and rate limiting system for LinkedIn scraping.

This module manages multiple LinkedIn accounts to distribute scraping load
and avoid rate limits. It tracks daily usage per account and rotates between
accounts when limits are reached.
"""

import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session


@dataclass
class LinkedInAccount:
    """
    Data class representing a LinkedIn account for scraping.
    
    Attributes:
        id: Unique identifier for the account (e.g., "1", "2")
        email: LinkedIn login email
        password: LinkedIn login password
        profiles_scraped_today: Number of profiles scraped today
        is_flagged: Whether account is flagged for security checkpoint
        last_used: Timestamp of last use
    """
    id: str
    email: str
    password: str
    profiles_scraped_today: int = 0
    is_flagged: bool = False
    last_used: Optional[datetime] = None


class AccountRotationManager:
    """
    Manages rotation of multiple LinkedIn accounts for scraping.
    
    Features:
    - Loads accounts from numbered environment variables
    - Tracks daily usage per account
    - Enforces daily scraping limits
    - Rotates to next available account when limit reached
    - Flags accounts that encounter security checkpoints
    - Resets counters at midnight UTC
    """
    
    def __init__(self, accounts: Optional[List[LinkedInAccount]] = None, daily_limit: Optional[int] = None):
        """
        Initialize the account rotation manager.
        
        Args:
            accounts: List of LinkedInAccount objects. If None, loads from environment.
            daily_limit: Maximum profiles per account per day. If None, reads from env.
        """
        if accounts is None:
            self.accounts = self._load_accounts_from_env()
        else:
            self.accounts = accounts
            
        if daily_limit is None:
            self.daily_limit = int(os.environ.get("SCRAPER_DAILY_LIMIT_PER_ACCOUNT", "80"))
        else:
            self.daily_limit = daily_limit
            
        self._current_index = 0
        self._load_usage_from_db()
    
    def _load_accounts_from_env(self) -> List[LinkedInAccount]:
        """
        Load LinkedIn accounts from numbered environment variables.
        
        Reads LINKEDIN_EMAIL_N and LINKEDIN_PASSWORD_N where N starts at 1
        and continues until a gap is found in the sequence.
        
        Returns:
            List of LinkedInAccount objects.
        
        Raises:
            ValueError: If no accounts are configured.
        """
        accounts = []
        n = 1
        
        while True:
            email_key = f"LINKEDIN_EMAIL_{n}"
            password_key = f"LINKEDIN_PASSWORD_{n}"
            
            email = os.environ.get(email_key)
            password = os.environ.get(password_key)
            
            # Stop when we hit a gap in the sequence
            if not email or not password:
                break
            
            account = LinkedInAccount(
                id=str(n),
                email=email,
                password=password,
                profiles_scraped_today=0,
                is_flagged=False,
                last_used=None
            )
            accounts.append(account)
            n += 1
        
        if not accounts:
            raise ValueError(
                "No LinkedIn accounts configured. "
                "Set LINKEDIN_EMAIL_1, LINKEDIN_PASSWORD_1, etc. in environment variables."
            )
        
        return accounts
    
    def _load_usage_from_db(self) -> None:
        """
        Load today's usage statistics from database for all accounts.
        
        Updates profiles_scraped_today and is_flagged for each account
        based on database records.
        """
        try:
            # Import here to avoid import-time database connection
            from ..database.connection import get_db
            from ..database.models import AccountUsage
            
            db = next(get_db())
            today = date.today()
            
            for account in self.accounts:
                usage = (
                    db.query(AccountUsage)
                    .filter(
                        AccountUsage.account_email == account.email,
                        AccountUsage.date == today
                    )
                    .first()
                )
                
                if usage:
                    account.profiles_scraped_today = usage.profiles_scraped
                    account.is_flagged = usage.is_flagged
                else:
                    account.profiles_scraped_today = 0
                    account.is_flagged = False
            
            db.close()
        except Exception as e:
            print(f"Warning: Could not load usage from database: {e}")
            # Continue with zero usage if database unavailable
    
    def get_next_account(self) -> Optional[LinkedInAccount]:
        """
        Get the next available account from the rotation pool.
        
        Selects an account that:
        - Is not flagged for security checkpoint
        - Has not reached the daily scraping limit
        
        Returns:
            LinkedInAccount object, or None if all accounts exhausted.
        """
        # Try each account starting from current index
        attempts = 0
        while attempts < len(self.accounts):
            account = self.accounts[self._current_index]
            
            # Move to next account for next call
            self._current_index = (self._current_index + 1) % len(self.accounts)
            attempts += 1
            
            # Check if account is available
            if not account.is_flagged and account.profiles_scraped_today < self.daily_limit:
                account.last_used = datetime.utcnow()
                return account
        
        # All accounts exhausted
        return None
    
    def mark_account_exhausted(self, account_email: str) -> None:
        """
        Mark an account as having reached its daily limit.
        
        Args:
            account_email: Email of the account to mark as exhausted.
        """
        for account in self.accounts:
            if account.email == account_email:
                account.profiles_scraped_today = self.daily_limit
                break
    
    def mark_account_flagged(self, account_email: str) -> None:
        """
        Mark an account as flagged for security checkpoint.
        
        Args:
            account_email: Email of the account to flag.
        """
        for account in self.accounts:
            if account.email == account_email:
                account.is_flagged = True
                break
        
        # Update database
        try:
            # Import here to avoid import-time database connection
            from ..database.connection import get_db
            from ..database.models import AccountUsage
            
            db = next(get_db())
            today = date.today()
            
            usage = (
                db.query(AccountUsage)
                .filter(
                    AccountUsage.account_email == account_email,
                    AccountUsage.date == today
                )
                .first()
            )
            
            if usage:
                usage.is_flagged = True
                usage.updated_at = datetime.utcnow()
            else:
                usage = AccountUsage(
                    account_email=account_email,
                    date=today,
                    profiles_scraped=0,
                    is_flagged=True
                )
                db.add(usage)
            
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Could not update flagged status in database: {e}")
    
    def increment_usage(self, account_email: str) -> None:
        """
        Increment the usage counter for an account.
        
        Updates both in-memory counter and database record.
        
        Args:
            account_email: Email of the account to increment.
        """
        # Update in-memory counter
        for account in self.accounts:
            if account.email == account_email:
                account.profiles_scraped_today += 1
                break
        
        # Update database
        try:
            # Import here to avoid import-time database connection
            from ..database.connection import get_db
            from ..database.models import AccountUsage
            
            db = next(get_db())
            today = date.today()
            
            usage = (
                db.query(AccountUsage)
                .filter(
                    AccountUsage.account_email == account_email,
                    AccountUsage.date == today
                )
                .first()
            )
            
            if usage:
                usage.profiles_scraped += 1
                usage.updated_at = datetime.utcnow()
            else:
                usage = AccountUsage(
                    account_email=account_email,
                    date=today,
                    profiles_scraped=1,
                    is_flagged=False
                )
                db.add(usage)
            
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Could not update usage in database: {e}")
    
    def reset_daily_counters(self) -> None:
        """
        Reset all account usage counters to zero.
        
        Should be called at midnight UTC to reset daily limits.
        Clears in-memory counters and unflag all accounts.
        Database records are preserved for historical tracking.
        """
        for account in self.accounts:
            account.profiles_scraped_today = 0
            account.is_flagged = False
    
    def get_usage_stats(self) -> dict:
        """
        Get usage statistics for all accounts.
        
        Returns:
            Dictionary with account emails as keys and usage info as values.
            Format: {
                "account@example.com": {
                    "profiles_scraped": 45,
                    "limit": 80,
                    "is_flagged": False,
                    "available": True
                }
            }
        """
        stats = {}
        
        for account in self.accounts:
            stats[account.email] = {
                "profiles_scraped": account.profiles_scraped_today,
                "limit": self.daily_limit,
                "is_flagged": account.is_flagged,
                "available": not account.is_flagged and account.profiles_scraped_today < self.daily_limit
            }
        
        return stats
    
    def get_total_available_capacity(self) -> int:
        """
        Get total number of profiles that can still be scraped today.
        
        Returns:
            Total remaining capacity across all available accounts.
        """
        total = 0
        
        for account in self.accounts:
            if not account.is_flagged:
                remaining = self.daily_limit - account.profiles_scraped_today
                if remaining > 0:
                    total += remaining
        
        return total
    
    def has_available_accounts(self) -> bool:
        """
        Check if any accounts are available for scraping.
        
        Returns:
            True if at least one account is available, False otherwise.
        """
        return self.get_next_account() is not None
