"""
Unit tests for CacheManager component.
Tests cache operations, eviction policy, and statistics.
"""
import pytest
from dxf_generator.services.cache_manager import CacheManager


class MockComponent:
    """Mock component for testing cache key generation."""
    def __init__(self, data):
        self.data = data


@pytest.fixture
def cache():
    """Create a fresh CacheManager instance for each test."""
    return CacheManager(max_size=5, name="test")


def test_cache_initialization(cache):
    """Test cache initializes with correct defaults."""
    assert cache.size == 0
    assert cache._max_size == 5
    assert cache._name == "test"


def test_get_key_generates_stable_keys():
    """Test that cache keys are stable and consistent."""
    cache = CacheManager()
    comp1 = MockComponent({"a": 1, "b": 2})
    comp2 = MockComponent({"a": 1, "b": 2})
    comp3 = MockComponent({"a": 1, "b": 3})  # Different data
    
    key1 = cache.get_key(comp1)
    key2 = cache.get_key(comp2)
    key3 = cache.get_key(comp3)
    
    assert key1 == key2, "Same data should produce same key"
    assert key1 != key3, "Different data should produce different key"
    assert "MockComponent" in key1


def test_set_and_get(cache):
    """Test basic set and get operations."""
    cache.set("key1", "value1")
    cache.set("key2", b"binary_data")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == b"binary_data"
    assert cache.size == 2


def test_get_returns_none_for_missing_key(cache):
    """Test get returns None for non-existent keys."""
    result = cache.get("nonexistent")
    assert result is None


def test_contains(cache):
    """Test contains method."""
    cache.set("exists", "value")
    
    assert cache.contains("exists") is True
    assert cache.contains("missing") is False


def test_cache_eviction_fifo(cache):
    """Test FIFO eviction when cache exceeds max size."""
    # Fill cache to limit (5)
    for i in range(5):
        cache.set(f"key{i}", f"value{i}")
    
    assert cache.size == 5
    assert cache.contains("key0")
    
    # Add one more - should evict key0 (FIFO)
    cache.set("key5", "value5")
    
    assert cache.size == 5
    assert not cache.contains("key0"), "First key should be evicted"
    assert cache.contains("key5"), "New key should exist"


def test_clear(cache):
    """Test cache clear operation."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.size == 2
    
    cache.clear()
    
    assert cache.size == 0
    assert not cache.contains("key1")


def test_stats_tracking(cache):
    """Test cache hit/miss statistics."""
    cache.set("key1", "value1")
    
    # Hit
    cache.get("key1")
    # Miss
    cache.get("nonexistent")
    cache.get("also_missing")
    
    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 2
    assert stats["size"] == 1
    assert "hit_rate" in stats


def test_stats_hit_rate_calculation():
    """Test hit rate percentage calculation."""
    cache = CacheManager(max_size=10, name="stats_test")
    cache.set("key", "value")
    
    # 3 hits
    for _ in range(3):
        cache.get("key")
    
    # 1 miss
    cache.get("missing")
    
    stats = cache.stats
    assert stats["hits"] == 3
    assert stats["misses"] == 1
    assert stats["hit_rate"] == "75.0%"


def test_large_cache():
    """Test cache with larger size limit."""
    cache = CacheManager(max_size=1000, name="large")
    
    for i in range(1000):
        cache.set(f"key{i}", f"value{i}")
    
    assert cache.size == 1000
    
    # Add one more
    cache.set("overflow", "data")
    assert cache.size == 1000
