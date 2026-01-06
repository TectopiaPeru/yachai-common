# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-05

### Added
- Initial release of yachai-common package
- Cache module with Redis support and memory fallback
  - CacheManager class for distributed caching
  - @cached and @async_cached decorators
  - Helper functions: get_cached, set_cached, delete_cached
- Security module with logging and data protection
  - SecureLogger for sanitized logging
  - Data sanitization and masking functions
  - Hash and verification utilities
  - Email and tenant ID validation
- Full test suite with pytest
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- PyPI publishing automation

### Features
- Redis connection with automatic failover to memory cache
- TTL support for cache entries
- Pattern-based cache clearing
- Automatic sensitive data detection and masking
- Configurable logging levels
- Cross-platform compatibility (Windows/Linux/Mac)

### Dependencies
- Redis >= 5.0.0
- cryptography >= 3.4.8
- email-validator >= 2.0.0

### Python Support
- Python 3.9+
- Tested on Python 3.9, 3.10, 3.11

---

## [Unreleased]

### Changes
- [List upcoming changes here]

---

## How to Use This Changelog

1. Add new entries under the "Unreleased" section
2. When releasing, move entries to the appropriate version section
3. Follow semantic versioning:
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes (backward compatible)
