"""Tests for security module."""

import pytest
from unittest.mock import Mock, patch

from yachai_common import (
    SecureLogger,
    get_secure_logger,
    hash_secret,
    mask_sensitive_data,
    sanitize_for_logging,
    validate_email,
    validate_tenant_id,
    verify_hash,
)


class TestSecurityFunctions:
    """Test security utility functions."""

    def test_sanitize_for_logging(self):
        """Test log sanitization."""
        # Test with sensitive data
        log_data = {
            "api_key": "sk-1234567890abcdef",
            "password": "secret123",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "safe_field": "this_is_safe"
        }
        
        result = sanitize_for_logging(log_data)
        
        assert "sk-1234" not in str(result)
        assert "secret123" not in str(result)
        assert "eyJhbGci" not in str(result)
        assert "this_is_safe" in str(result)
        assert "***" in str(result)

    def test_mask_sensitive_data(self):
        """Test data masking."""
        # Test email
        assert mask_sensitive_data("user@example.com", "email") == "us***@example.com"
        
        # Test phone
        assert mask_sensitive_data("+1234567890", "phone") == "+******7890"
        
        # Test generic secret
        assert mask_sensitive_data("secret_key_123", "secret") == "sec***123"

    def test_hash_secret(self):
        """Test secret hashing."""
        secret = "test_secret"
        hashed = hash_secret(secret)
        
        # Should be different from original
        assert hashed != secret
        
        # Should be consistent
        assert hash_secret(secret) == hashed
        
        # Should include algorithm and salt
        assert ":" in hashed
        assert len(hashed) > 20

    def test_verify_hash(self):
        """Test hash verification."""
        secret = "test_secret"
        hashed = hash_secret(secret)
        
        # Correct verification
        assert verify_hash(secret, hashed) is True
        
        # Incorrect verification
        assert verify_hash("wrong_secret", hashed) is False

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("test.email+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validate_email("invalid") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("user..name@domain.com") is False

    def test_validate_tenant_id(self):
        """Test tenant ID validation."""
        # Valid tenant IDs
        assert validate_tenant_id("cotizai") is True
        assert validate_tenant_id("tectopia") is True
        assert validate_tenant_id("salud_inteligente") is True
        
        # Invalid tenant IDs
        assert validate_tenant_id("") is False
        assert validate_tenant_id("Tenant-Name") is False  # uppercase
        assert validate_tenant_id("tenant_name!") is False  # special char
        assert validate_tenant_id("a" * 101) is False  # too long


class TestSecureLogger:
    """Test SecureLogger class."""

    def test_secure_logger_sanitizes(self):
        """Test that SecureLogger sanitizes logs."""
        logger = SecureLogger("test_logger")
        
        # Mock the underlying logger
        with patch.object(logger.logger, "info") as mock_info:
            logger.info({"api_key": "secret_value", "safe": "data"})
            
            # Check that info was called
            mock_info.assert_called_once()
            
            # Check that the call was sanitized
            call_args = mock_info.call_args[0][0]
            assert "secret_value" not in str(call_args)
            assert "***" in str(call_args)

    def test_get_secure_logger(self):
        """Test get_secure_logger helper."""
        logger = get_secure_logger("test")
        assert isinstance(logger, SecureLogger)
        assert logger.logger.name == "test"

    def test_all_logger_methods(self):
        """Test all logging methods are available."""
        logger = SecureLogger("test")
        
        with patch.object(logger.logger, "info") as mock_info, \
             patch.object(logger.logger, "error") as mock_error, \
             patch.object(logger.logger, "warning") as mock_warning, \
             patch.object(logger.logger, "debug") as mock_debug:
            
            logger.info("info message")
            logger.error("error message")
            logger.warning("warning message")
            logger.debug("debug message")
            
            mock_info.assert_called_once()
            mock_error.assert_called_once()
            mock_warning.assert_called_once()
            mock_debug.assert_called_once()
