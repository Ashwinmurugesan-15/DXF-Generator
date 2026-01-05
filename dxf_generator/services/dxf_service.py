from concurrent.futures import ThreadPoolExecutor, as_completed  # Used to run DXF generation tasks concurrently
import ezdxf  # DXF library for reading/writing DXF files
from typing import Dict, Any
import functools
import hashlib
from dxf_generator.config.env_config import config

class DXFService:
    _executor = ThreadPoolExecutor(max_workers=config.MAX_THREADS)  # Thread pool from environment config
    _parse_cache = {}  # Simple in-memory cache for parsed files
    _generation_cache = {}  # Cache for generated DXF binary content

    @classmethod
    def save_cached(cls, component, filename: str) -> bytes:
        """
        Generate DXF with caching. If parameters are identical, returns cached bytes.
        """
        # Create a unique key based on component data
        cache_key = f"{component.__class__.__name__}_{hash(frozenset(component.data.items()))}"
        
        if cache_key in cls._generation_cache:
            return cls._generation_cache[cache_key]
        
        # Generate to a temporary path or handle in-memory
        # For simplicity with ezdxf, we still save to disk then read back
        component.generate_dxf(filename)
        with open(filename, 'rb') as f:
            content = f.read()
            
        cls._generation_cache[cache_key] = content
        # Eviction
        if len(cls._generation_cache) > 100:
            cls._generation_cache.pop(next(iter(cls._generation_cache)))
            
        return content

    @staticmethod
    def save(component, filename: str):
        # Generate DXF for a single component (synchronous execution)
        component.generate_dxf(filename)
        return filename  # Return generated file path

    @classmethod
    def save_batch(cls, components: list, filenames: list):
        """
        Generate multiple DXF files concurrently.
        """
        futures = []  # Holds references to submitted background tasks

        # Submit DXF generation tasks to the thread pool
        for component, filename in zip(components, filenames):
            futures.append(
                cls._executor.submit(component.generate_dxf, filename)
            )

        generated_files = []  # Stores successfully generated file names

        # Wait for all threads to complete and collect results
        for future, filename in zip(futures, filenames):
            future.result()  # Blocks until this DXF generation finishes
            generated_files.append(filename)

        return generated_files  # Return list of generated DXF files

    @staticmethod
    def _get_file_hash(filepath: str) -> str:
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def parse(cls, filepath: str) -> Dict[str, Any]:
        """
        Parses a DXF file and extracts dimensions for I-Beam or Column.
        Uses an internal cache to avoid re-parsing the same file content.
        """
        try:
            file_hash = cls._get_file_hash(filepath)
            if file_hash in cls._parse_cache:
                return cls._parse_cache[file_hash]

            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            # ... rest of the logic ...
            polylines = msp.query('LWPOLYLINE')
            if not polylines:
                raise ValueError("No LWPOLYLINE found in DXF")
            
            polyline = polylines[0]
            points = list(polyline.get_points())
            
            result = None
            # I-Beam has 12 or 13 points (if closed)
            if len(points) in [12, 13]:
                b = points[1][0]
                tf = points[2][1]
                h = points[6][1]
                tw = 2 * points[4][0] - b
                
                result = {
                    "type": "ibeam",
                    "data": {
                        "total_depth": round(float(h), 2),
                        "flange_width": round(float(b), 2),
                        "web_thickness": round(float(tw), 2),
                        "flange_thickness": round(float(tf), 2)
                    }
                }
            
            # Column has 4 or 5 points (if closed)
            elif len(points) in [4, 5]:
                width = points[1][0]
                height = points[2][1]
                
                result = {
                    "type": "column",
                    "data": {
                        "width": round(float(width), 2),
                        "height": round(float(height), 2)
                    }
                }
            
            if result:
                # Cache the result before returning
                cls._parse_cache[file_hash] = result
                # Keep cache size reasonable (simple eviction)
                if len(cls._parse_cache) > 100:
                    cls._parse_cache.pop(next(iter(cls._parse_cache)))
                return result
            
            raise ValueError(f"Unexpected number of vertices ({len(points)}). Only standard I-Beams and Columns are supported.")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse DXF: {str(e)}")
