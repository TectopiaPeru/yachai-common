"""
YACHAI Common - Shared utilities for YACHAI projects.
"""

__version__ = "1.0.0"
__author__ = "YACHAI Team"

from .cache import (
    CacheManager,
    cache_manager,
    cached,
    async_cached,
    get_cached,
    set_cached,
    delete_cached,
    clear_cache_pattern,
)

from .security import (
    sanitize_for_logging,
    hash_secret,
    verify_hash,
    validate_email,
    validate_tenant_id,
    mask_sensitive_data,
    SecureLogger,
    get_secure_logger,
)

__all__ = [
    # Cache
    "CacheManager",
    "cache_manager",
    "cached",
    "async_cached",
    "get_cached",
    "set_cached",
    "delete_cached",
    "clear_cache_pattern",
    # Security
    "sanitize_for_logging",
    "hash_secret",
    "verify_hash",
    "validate_email",
    "validate_tenant_id",
    "mask_sensitive_data",
    "SecureLogger",
    "get_secure_logger",
]
