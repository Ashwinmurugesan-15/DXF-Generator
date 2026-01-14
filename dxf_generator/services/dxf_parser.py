"""
DXFParser - Handles DXF file parsing and dimension extraction.
Single Responsibility: Read DXF files, identify shapes, extract dimensions.
"""
import ezdxf
import hashlib
from typing import Dict, Any
from dxf_generator.config.logging_config import logger


class DXFParser:
    """
    Parses DXF files and extracts structural dimensions.
    Supports I-Beam and Column profile identification.
    """
    
    @staticmethod
    def get_file_hash(filepath: str) -> str:
        """
        Calculate MD5 hash of a file for cache key generation.
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hex digest
        """
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    @classmethod
    def parse(cls, filepath: str) -> Dict[str, Any]:
        """
        Parse a DXF file and extract dimensions.
        
        Args:
            filepath: Path to DXF file
            
        Returns:
            Dict with 'type' (ibeam/column) and 'data' (dimensions)
            
        Raises:
            ValueError: If file cannot be parsed or has invalid structure
            ezdxf.DXFError: If file is corrupt or invalid DXF
        """
        logger.debug(f"Parsing DXF file: {filepath}")
        
        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            polylines = msp.query('LWPOLYLINE')
            if not polylines:
                logger.warning(f"No LWPOLYLINE found in: {filepath}")
                raise ValueError("No LWPOLYLINE found in DXF")
            
            logger.debug(f"Found {len(polylines)} polylines")
            
            polyline = polylines[0]
            points = list(polyline.get_points())
            
            return cls._identify_shape(points, filepath)
            
        except ezdxf.DXFError as e:
            logger.error(f"DXF parsing error: {e}")
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing {filepath}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse DXF: {str(e)}") from e
    
    @classmethod
    def _identify_shape(cls, points: list, filepath: str) -> Dict[str, Any]:
        """
        Identify shape type from polyline vertices and extract dimensions.
        
        Args:
            points: List of vertex points
            filepath: Source file path (for logging)
            
        Returns:
            Dict with shape type and dimensions
        """
        num_points = len(points)
        
        # I-Beam has 12 or 13 points (if closed)
        if num_points in [12, 13]:
            return cls._parse_ibeam(points)
        
        # Column has 4 or 5 points (if closed)
        elif num_points in [4, 5]:
            return cls._parse_column(points)
        
        logger.warning(f"Unexpected vertex count ({num_points}) in {filepath}")
        raise ValueError(
            f"Unexpected number of vertices ({num_points}). "
            "Only standard I-Beams and Columns are supported."
        )
    
    @staticmethod
    def _parse_ibeam(points: list) -> Dict[str, Any]:
        """Extract I-Beam dimensions from vertices."""
        b = points[1][0]   # flange width
        tf = points[2][1]  # flange thickness
        h = points[6][1]   # total depth
        tw = 2 * points[4][0] - b  # web thickness
        
        result = {
            "type": "ibeam",
            "data": {
                "total_depth": round(float(h), 2),
                "flange_width": round(float(b), 2),
                "web_thickness": round(float(tw), 2),
                "flange_thickness": round(float(tf), 2)
            }
        }
        logger.info(f"Parsed I-Beam: {result['data']}")
        return result
    
    @staticmethod
    def _parse_column(points: list) -> Dict[str, Any]:
        """Extract Column dimensions from vertices."""
        width = points[1][0]
        height = points[2][1]
        
        result = {
            "type": "column",
            "data": {
                "width": round(float(width), 2),
                "height": round(float(height), 2)
            }
        }
        logger.info(f"Parsed Column: {result['data']}")
        return result
