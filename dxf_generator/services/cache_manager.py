"""
CacheManager - Handles in-memory caching with eviction policy.
Single Responsibility: Cache storage, key generation, and eviction.
"""
from typing import Any, Optional
import threading
from dxf_generator.config.logging_config import logger


class CacheManager:
    """
    Manages in-memory cache with configurable size limits.
    Implements simple FIFO eviction when cache exceeds max size.
    """
    
    def __init__(self, max_size: int = 500, name: str = "default"):
        self._cache: dict = {}
        self._max_size = max_size
        self._name = name
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()
    
    def get_key(self, obj: Any) -> str:
        """
        Generate a stable cache key from an object.
        
        Args:
            obj: Object with 'data' attribute (dict) and __class__.__name__
            
        Returns:
            String cache key
        """
        class_name = obj.__class__.__name__
        # Sort keys for stable hash
        data_hash = hash(frozenset(sorted(obj.data.items())))
        return f"{class_name}_{data_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache (Thread-Safe).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        with self._lock:
            if key in self._cache:
                self._hits += 1
                logger.debug(f"[{self._name}] Cache hit: {key}")
                return self._cache[key]
            
            self._misses += 1
            logger.debug(f"[{self._name}] Cache miss: {key}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store item in cache with eviction if needed (Thread-Safe).
        
        Args:
            key: Cache key
            value: Value to store
        """
        with self._lock:
            self._cache[key] = value
            
            # FIFO eviction if over limit
            if len(self._cache) > self._max_size:
                evicted_key = next(iter(self._cache))
                self._cache.pop(evicted_key)
                logger.debug(f"[{self._name}] Cache eviction: {evicted_key}")
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache (Thread-Safe)."""
        with self._lock:
            return key in self._cache
    
    def clear(self) -> None:
        """Clear all cached items (Thread-Safe)."""
        with self._lock:
            self._cache.clear()
            logger.info(f"[{self._name}] Cache cleared")
    
    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self._cache)
    
    @property
    def stats(self) -> dict:
        """Cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": self.size,
            "hit_rate": f"{hit_rate:.1f}%"
        }
