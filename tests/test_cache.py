"""Tests for cache module."""

import pytest
from unittest.mock import Mock, patch

from yachai_common import (
    CacheManager,
    cached,
    delete_cached,
    get_cache_stats,
    get_cached,
    set_cached,
)


class TestCacheManager:
    """Test CacheManager class."""

    def test_init_with_redis(self):
        """Test initialization with Redis."""
        with patch("yachai_common.cache.redis.Redis"):
            manager = CacheManager(redis_url="redis://localhost:6379/0")
            assert manager.redis_client is not None

    def test_init_without_redis(self):
        """Test initialization without Redis (memory fallback)."""
        manager = CacheManager()
        assert manager.redis_client is None
        assert manager._memory_cache == {}

    def test_set_and_get_with_redis(self):
        """Test set and get operations with Redis."""
        mock_redis = Mock()
        mock_redis.get.return_value = b'"test_value"'
        mock_redis.setex.return_value = True

        with patch("yachai_common.cache.redis.Redis", return_value=mock_redis):
            manager = CacheManager(redis_url="redis://localhost:6379/0")
            
            # Set value
            manager.set("test_key", "test_value", ttl=60)
            mock_redis.setex.assert_called_once()
            
            # Get value
            result = manager.get("test_key")
            assert result == "test_value"

    def test_set_and_get_memory(self):
        """Test set and get operations with memory cache."""
        manager = CacheManager()
        
        # Set value
        manager.set("test_key", "test_value", ttl=60)
        assert "test_key" in manager._memory_cache
        
        # Get value
        result = manager.get("test_key")
        assert result == "test_value"

    def test_delete(self):
        """Test delete operation."""
        mock_redis = Mock()
        mock_redis.delete.return_value = 1

        with patch("yachai_common.cache.redis.Redis", return_value=mock_redis):
            manager = CacheManager(redis_url="redis://localhost:6379/0")
            manager.delete("test_key")
            mock_redis.delete.assert_called_once_with("test_key")

    def test_clear_pattern(self):
        """Test clear pattern operation."""
        mock_redis = Mock()
        mock_redis.scan_iter.return_value = ["key1", "key2"]
        mock_redis.delete.return_value = 2

        with patch("yachai_common.cache.redis.Redis", return_value=mock_redis):
            manager = CacheManager(redis_url="redis://localhost:6379/0")
            manager.clear_pattern("test:*")
            mock_redis.scan_iter.assert_called_once_with(match="test:*")
            assert mock_redis.delete.call_count == 1


class TestCacheDecorators:
    """Test cache decorators."""

    def test_cached_decorator_sync(self):
        """Test @cached decorator for sync functions."""
        manager = Mock()
        manager.get.return_value = None
        manager.set.return_value = True

        with patch("yachai_common.cache.cache_manager", manager):
            @cached(ttl=60, key_prefix="test")
            def test_func(x):
                return x * 2

            result = test_func(5)
            assert result == 10
            manager.set.assert_called_once()

    def test_cached_decorator_async(self):
        """Test @cached decorator for async functions."""
        manager = Mock()
        manager.get.return_value = None
        manager.set.return_value = True

        with patch("yachai_common.cache.cache_manager", manager):
            @cached(ttl=60, key_prefix="test")
            async def test_func(x):
                return x * 2

            # Test async function
            import asyncio
            result = asyncio.run(test_func(5))
            assert result == 10
            manager.set.assert_called_once()

    def test_get_cached_helper(self):
        """Test get_cached helper function."""
        with patch("yachai_common.cache.cache_manager") as mock_manager:
            mock_manager.get.return_value = "test_value"
            result = get_cached("test_key")
            assert result == "test_value"
            mock_manager.get.assert_called_once_with("test_key", default=None)

    def test_set_cached_helper(self):
        """Test set_cached helper function."""
        with patch("yachai_common.cache.cache_manager") as mock_manager:
            set_cached("test_key", "test_value", ttl=60)
            mock_manager.set.assert_called_once_with("test_key", "test_value", ttl=60)

    def test_delete_cached_helper(self):
        """Test delete_cached helper function."""
        with patch("yachai_common.cache.cache_manager") as mock_manager:
            delete_cached("test_key")
            mock_manager.delete.assert_called_once_with("test_key")

    def test_get_cache_stats_helper(self):
        """Test get_cache_stats helper function."""
        with patch("yachai_common.cache.cache_manager") as mock_manager:
            mock_manager.get_stats.return_value = {"hits": 10, "misses": 5}
            result = get_cache_stats()
            assert result == {"hits": 10, "misses": 5}
            mock_manager.get_stats.assert_called_once()
