"""
Error handling utilities for the Alumni Management System.

Provides centralized error handling, logging, and user-friendly error messages.
"""

import logging
import traceback
from typing import Optional, Dict, Any
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ErrorCategory(Enum):
    """Categories of errors in the system."""
    DATABASE = "database"
    NETWORK = "network"
    SCRAPING = "scraping"
    STORAGE = "storage"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"  # System cannot function
    ERROR = "error"        # Operation failed but system continues
    WARNING = "warning"    # Potential issue
    INFO = "info"          # Normal operations


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Name of the module (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_error(
    logger: logging.Logger,
    error: Exception,
    category: ErrorCategory,
    severity: ErrorSeverity,
    context: Optional[Dict[str, Any]] = None,
    include_traceback: bool = True
) -> None:
    """
    Log an error with appropriate context and severity.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        category: Category of error
        severity: Severity level
        context: Additional context (alumni_id, account_email, etc.)
        include_traceback: Whether to include full traceback
    """
    error_msg = f"[{category.value.upper()}] {str(error)}"
    
    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        error_msg = f"{error_msg} | Context: {context_str}"
    
    if severity == ErrorSeverity.CRITICAL:
        logger.critical(error_msg)
    elif severity == ErrorSeverity.ERROR:
        logger.error(error_msg)
    elif severity == ErrorSeverity.WARNING:
        logger.warning(error_msg)
    else:
        logger.info(error_msg)
    
    if include_traceback and severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR]:
        logger.debug(traceback.format_exc())


def get_user_friendly_error_message(
    error: Exception,
    category: ErrorCategory,
    default_message: Optional[str] = None
) -> str:
    """
    Convert technical error to user-friendly message.
    
    Args:
        error: Exception that occurred
        category: Category of error
        default_message: Default message if no specific mapping exists
    
    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()
    
    # Database errors
    if category == ErrorCategory.DATABASE:
        if "connection" in error_str or "connect" in error_str:
            return "Unable to connect to the database. Please check your database configuration."
        elif "timeout" in error_str:
            return "Database operation timed out. Please try again."
        elif "duplicate" in error_str or "unique" in error_str:
            return "This record already exists. Please use a different identifier."
        elif "foreign key" in error_str:
            return "Cannot delete this record because it is referenced by other records."
        else:
            return "A database error occurred. Please try again or contact support."
    
    # Network errors
    elif category == ErrorCategory.NETWORK:
        if "timeout" in error_str:
            return "The request timed out. Please check your internet connection and try again."
        elif "connection" in error_str:
            return "Unable to establish connection. Please check your internet connection."
        elif "dns" in error_str or "resolve" in error_str:
            return "Unable to resolve the server address. Please check your network settings."
        else:
            return "A network error occurred. Please check your connection and try again."
    
    # Scraping errors
    elif category == ErrorCategory.SCRAPING:
        if "checkpoint" in error_str or "challenge" in error_str:
            return "LinkedIn security checkpoint detected. The account has been flagged for manual verification."
        elif "login" in error_str or "authentication" in error_str:
            return "Failed to log in to LinkedIn. Please check your credentials."
        elif "rate limit" in error_str or "too many requests" in error_str:
            return "Rate limit reached. Please try again later."
        elif "not found" in error_str or "404" in error_str:
            return "LinkedIn profile not found. Please check the URL."
        else:
            return "Failed to scrape LinkedIn profile. Please try again later."
    
    # Storage errors
    elif category == ErrorCategory.STORAGE:
        if "authentication" in error_str or "credentials" in error_str:
            return "Storage authentication failed. Please check your B2 credentials."
        elif "bucket" in error_str:
            return "Storage bucket not found. Please check your B2 configuration."
        elif "quota" in error_str or "limit" in error_str:
            return "Storage quota exceeded. Please contact your administrator."
        else:
            return "Failed to upload file to storage. The data has been saved to the database."
    
    # Validation errors
    elif category == ErrorCategory.VALIDATION:
        return f"Validation error: {str(error)}"
    
    # Configuration errors
    elif category == ErrorCategory.CONFIGURATION:
        if "environment" in error_str or "variable" in error_str:
            return "Configuration error: Required environment variable is missing."
        else:
            return f"Configuration error: {str(error)}"
    
    # Default
    return default_message or "An unexpected error occurred. Please try again or contact support."


def handle_database_connection_error(logger: logging.Logger, error: Exception) -> Dict[str, Any]:
    """
    Handle database connection errors with appropriate logging and user message.
    
    Args:
        logger: Logger instance
        error: Database connection error
    
    Returns:
        Dictionary with error info and user message
    """
    log_error(
        logger,
        error,
        ErrorCategory.DATABASE,
        ErrorSeverity.CRITICAL,
        context={"operation": "database_connection"}
    )
    
    return {
        "error": True,
        "category": "database",
        "severity": "critical",
        "user_message": get_user_friendly_error_message(error, ErrorCategory.DATABASE),
        "technical_message": str(error),
        "demo_mode": True
    }


def handle_scraping_error(
    logger: logging.Logger,
    error: Exception,
    alumni_id: Optional[int] = None,
    account_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle scraping errors with appropriate logging and user message.
    
    Args:
        logger: Logger instance
        error: Scraping error
        alumni_id: ID of alumni being scraped
        account_email: Email of account being used
    
    Returns:
        Dictionary with error info and user message
    """
    context = {}
    if alumni_id:
        context["alumni_id"] = alumni_id
    if account_email:
        context["account_email"] = account_email
    
    # Determine if it's a checkpoint error
    is_checkpoint = "checkpoint" in str(error).lower() or "challenge" in str(error).lower()
    
    log_error(
        logger,
        error,
        ErrorCategory.SCRAPING,
        ErrorSeverity.WARNING if is_checkpoint else ErrorSeverity.ERROR,
        context=context
    )
    
    return {
        "error": True,
        "category": "scraping",
        "severity": "warning" if is_checkpoint else "error",
        "user_message": get_user_friendly_error_message(error, ErrorCategory.SCRAPING),
        "technical_message": str(error),
        "is_checkpoint": is_checkpoint,
        "continue_processing": True  # Don't stop batch processing
    }


def handle_storage_error(
    logger: logging.Logger,
    error: Exception,
    alumni_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Handle storage (B2) errors with appropriate logging and user message.
    
    Args:
        logger: Logger instance
        error: Storage error
        alumni_id: ID of alumni whose PDF failed to upload
    
    Returns:
        Dictionary with error info and user message
    """
    context = {}
    if alumni_id:
        context["alumni_id"] = alumni_id
    
    log_error(
        logger,
        error,
        ErrorCategory.STORAGE,
        ErrorSeverity.WARNING,  # Storage failures are warnings, not errors
        context=context
    )
    
    return {
        "error": True,
        "category": "storage",
        "severity": "warning",
        "user_message": get_user_friendly_error_message(error, ErrorCategory.STORAGE),
        "technical_message": str(error),
        "continue_processing": True,  # Don't stop scraping
        "database_saved": True  # Database save should have succeeded
    }


def handle_chatbot_error(logger: logging.Logger, error: Exception, query: str) -> Dict[str, Any]:
    """
    Handle chatbot errors with appropriate logging and user message.
    
    Args:
        logger: Logger instance
        error: Chatbot error
        query: User's query that caused the error
    
    Returns:
        Dictionary with error info and user message
    """
    log_error(
        logger,
        error,
        ErrorCategory.DATABASE if "database" in str(error).lower() else ErrorCategory.UNKNOWN,
        ErrorSeverity.ERROR,
        context={"query": query}
    )
    
    user_message = (
        "I encountered an error while processing your query. "
        "Please try rephrasing your question or use the search interface instead."
    )
    
    return {
        "error": True,
        "category": "chatbot",
        "severity": "error",
        "user_message": user_message,
        "technical_message": str(error),
        "response": user_message,
        "alumni": [],
        "count": 0
    }


def get_account_exhaustion_message(reset_time: str = "midnight UTC") -> str:
    """
    Get user-friendly message for account exhaustion.
    
    Args:
        reset_time: Time when accounts will reset
    
    Returns:
        User-friendly message
    """
    return (
        f"⚠️ Daily scraping limit reached for all accounts. "
        f"Scraping will automatically resume at {reset_time}. "
        f"If you need to scrape urgently, please add more LinkedIn accounts "
        f"or wait for the daily limit to reset."
    )


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        error: Exception to check
    
    Returns:
        True if error is retryable, False otherwise
    """
    error_str = str(error).lower()
    
    # Non-retryable errors
    non_retryable = [
        "checkpoint",
        "challenge",
        "authentication failed",
        "invalid credentials",
        "not found",
        "404",
        "forbidden",
        "403"
    ]
    
    for pattern in non_retryable:
        if pattern in error_str:
            return False
    
    # Retryable errors
    retryable = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "503",
        "502",
        "500"
    ]
    
    for pattern in retryable:
        if pattern in error_str:
            return True
    
    # Default to retryable for unknown errors
    return True
