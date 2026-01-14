"""
DXFService - Simplified facade coordinating specialized components.
Single Responsibility: Provide unified API for routes, delegate to focused components.
"""
from typing import Dict, Any, List, Optional
import hashlib
from dxf_generator.services.cache_manager import CacheManager
from dxf_generator.services.batch_processor import BatchProcessor
from dxf_generator.services.dxf_parser import DXFParser
from dxf_generator.services.dxf_generator import DXFGenerator
from dxf_generator.config.logging_config import logger


class DXFService:
    """
    Facade service coordinating DXF generation and parsing.
    Delegates responsibilities to specialized components.
    """
    
    # Component instances (shared across service)
    _generation_cache = CacheManager(max_size=500, name="generation")
    _parse_cache = CacheManager(max_size=100, name="parse")
    _batch_cache = CacheManager(max_size=50, name="batch")  # Cache for full ZIP results
    _batch_processor = BatchProcessor()
    
    @classmethod
    def get_cache_key(cls, component) -> str:
        """Generate cache key for a component."""
        return cls._generation_cache.get_key(component)
    
    @classmethod
    def save(cls, component, filename: str) -> str:
        """
        Generate DXF for a single component (synchronous).
        
        Args:
            component: Component with generate_dxf method
            filename: Output file path
            
        Returns:
            Generated file path
        """
        DXFGenerator.generate(component, filename)
        return filename
    
    @classmethod
    def save_cached(cls, component, filename: str) -> bytes:
        """
        Generate DXF with caching support.
        
        Args:
            component: Component with generate_dxf method
            filename: Output file path
            
        Returns:
            DXF content as bytes
        """
        cache_key = cls._generation_cache.get_key(component)
        
        # Check cache
        cached = cls._generation_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            return cached
        
        # Generate and cache
        logger.info(f"Cache miss for {cache_key}. Generating...")
        content = DXFGenerator.generate(component, filename)
        cls._generation_cache.set(cache_key, content)
        
        return content
    
    @classmethod
    def save_batch(cls, components: List, filenames: List[str]) -> List[str]:
        """
        Generate multiple DXF files concurrently (fire-and-forget).
        """
        cache_hits = []

        def on_complete():
            logger.info("Background task completed")

        def on_error(exc):
            logger.error(f"Background task failed: {exc}")

        for component, filename in zip(components, filenames):
            cache_key = cls._generation_cache.get_key(component)
            cached = cls._generation_cache.get(cache_key)

            if cached:
                DXFGenerator.write_content(cached, filename)
                cache_hits.append(filename)
            else:
                cls._batch_processor.submit(
                    cls.save_cached,
                    component,
                    filename,
                    on_success=on_complete,
                    on_error=on_error
                )

        logger.info(
            f"Batch: {len(cache_hits)} cache hits, "
            f"{len(components) - len(cache_hits)} tasks queued"
        )

        return cache_hits
    
    @classmethod
    def parse(cls, filepath: str) -> Dict[str, Any]:
        """
        Parse a DXF file with caching.
        
        Args:
            filepath: Path to DXF file
            
        Returns:
            Dict with 'type' and 'data' keys
        """
        # Check cache
        file_hash = DXFParser.get_file_hash(filepath)
        cached = cls._parse_cache.get(file_hash)
        if cached:
            return cached
        
        # Parse and cache
        result = DXFParser.parse(filepath)
        cls._parse_cache.set(file_hash, result)
        
        return result
    
    @classmethod
    def get_batch_key(cls, components: List[Any]) -> str:
        """
        Generate a unique cache key for a batch of components.
        Sorts individual keys to ensure order independence.
        """
        keys = [cls._generation_cache.get_key(comp) for comp in components]
        keys.sort()
        # Hash the sorted list of keys
        batch_hash = hashlib.md5("".join(keys).encode()).hexdigest()
        return f"batch_{batch_hash}"

    @classmethod
    def get_cached_batch(cls, batch_key: str) -> Optional[bytes]:
        """Retrieve cached batch ZIP content."""
        return cls._batch_cache.get(batch_key)

    @classmethod
    def cache_batch(cls, batch_key: str, content: bytes) -> None:
        """Cache batch ZIP content."""
        cls._batch_cache.set(batch_key, content)

    # Expose cache for testing/debugging
    @classmethod
    def clear_caches(cls) -> None:
        """Clear all caches."""
        cls._generation_cache.clear()
        cls._parse_cache.clear()
        cls._batch_cache.clear()
    
    @classmethod
    def get_cache_stats(cls) -> dict:
        """Get cache statistics."""
        return {
            "generation": cls._generation_cache.stats,
            "parse": cls._parse_cache.stats,
            "batch": cls._batch_cache.stats
        }


        

