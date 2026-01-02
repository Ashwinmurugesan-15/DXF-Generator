import ezdxf

class DXFDrawing:
    def __init__(self):
        # Create a new DXF document and modelspace
        self.doc = ezdxf.new()
        self.msp = self.doc.modelspace()

    def draw_ibeam(self, data: dict):
        """
        Draw an I-Beam cross-section
        """
        h = data["total_depth"]
        b = data["flange_width"]
        tw = data["web_thickness"]
        tf = data["flange_thickness"]

        # Points for I-Beam profile (starting from bottom-left outer corner)
        points = [
            (0, 0),                            # 1: Bottom flange bottom-left
            (b, 0),                            # 2: Bottom flange bottom-right
            (b, tf),                           # 3: Bottom flange top-right
            ((b + tw) / 2, tf),                # 4: Web bottom-right
            ((b + tw) / 2, h - tf),            # 5: Web top-right
            (b, h - tf),                       # 6: Top flange bottom-right
            (b, h),                            # 7: Top flange top-right
            (0, h),                            # 8: Top flange top-left
            (0, h - tf),                       # 9: Top flange bottom-left
            ((b - tw) / 2, h - tf),            # 10: Web top-left
            ((b - tw) / 2, tf),                # 11: Web bottom-left
            (0, tf),                           # 12: Bottom flange top-left
            (0, 0)                             # Close
        ]

        self.msp.add_lwpolyline(points, close=True)

    def draw_column(self, data: dict):
        """
        Draw a column as a rectangular profile
        """
        width = data["width"]
        height = data["height"]

        points = [
            (0, 0),
            (width, 0),
            (width, height),
            (0, height),
            (0, 0)
        ]

        self.msp.add_lwpolyline(points, close=True)

    def save(self, filepath: str):
        """
        Save DXF file to disk
        """
        self.doc.saveas(filepath)
