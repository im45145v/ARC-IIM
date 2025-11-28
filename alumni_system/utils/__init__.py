"""
Utility modules for the Alumni Management System.
"""

from .error_handling import (
    ErrorCategory,
    ErrorSeverity,
    get_logger,
    log_error,
    get_user_friendly_error_message,
    handle_database_connection_error,
    handle_scraping_error,
    handle_storage_error,
    handle_chatbot_error,
    get_account_exhaustion_message,
    is_retryable_error,
)

__all__ = [
    "ErrorCategory",
    "ErrorSeverity",
    "get_logger",
    "log_error",
    "get_user_friendly_error_message",
    "handle_database_connection_error",
    "handle_scraping_error",
    "handle_storage_error",
    "handle_chatbot_error",
    "get_account_exhaustion_message",
    "is_retryable_error",
]
