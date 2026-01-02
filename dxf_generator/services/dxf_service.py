from concurrent.futures import ThreadPoolExecutor, as_completed  # Used to run DXF generation tasks concurrently
import ezdxf  # DXF library for reading/writing DXF files
from typing import Dict, Any

class DXFService:
    _executor = ThreadPoolExecutor(max_workers=8)  # Thread pool to handle multiple DXF generations in parallel

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
    def parse(filepath: str) -> Dict[str, Any]:
        """
        Parses a DXF file and extracts dimensions for I-Beam or Column.
        Analyzes LWPOLYLINE geometry to identify component type and dimensions.
        """
        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            # Find the main profile (assuming it's the first LWPOLYLINE)
            polylines = msp.query('LWPOLYLINE')
            if not polylines:
                raise ValueError("No LWPOLYLINE found in DXF")
            
            polyline = polylines[0]
            points = list(polyline.get_points())
            
            # LWPOLYLINE points are usually (x, y, start_width, end_width, bulge)
            
            # I-Beam has 12 or 13 points (if closed)
            if len(points) in [12, 13]:
                # Extract I-Beam dimensions based on drawing.py logic
                # b (flange_width) is at points[1][0]
                # tf (flange_thickness) is at points[2][1]
                # h (total_depth) is at points[6][1]
                # tw (web_thickness) is derived: points[4][0] = (b+tw)/2 => tw = 2*points[4][0] - b
                b = points[1][0]
                tf = points[2][1]
                h = points[6][1]
                tw = 2 * points[4][0] - b
                
                return {
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
                # Extract Column dimensions: points[1][0] is width, points[2][1] is height
                width = points[1][0]
                height = points[2][1]
                
                return {
                    "type": "column",
                    "data": {
                        "width": round(float(width), 2),
                        "height": round(float(height), 2)
                    }
                }
            
            else:
                raise ValueError(f"Unexpected number of vertices ({len(points)}). Only standard I-Beams and Columns are supported.")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse DXF: {str(e)}")
