from dxf_generator.config.env_config import config

# Global engineering tolerances (mm)

# --- Maximum Limits ---
MAX_IBEAM_LENGTH_MM = 18000     # Maximum practical I-beam length
MAX_IBEAM_WIDTH_MM = 1000      # Maximum flange width
MAX_IBEAM_DEPTH_MM = config.MAX_IBEAM_DEPTH_MM      # Maximum total depth (from env config)

# --- Minimum Limits ---
MIN_IBEAM_DEPTH_MM = 80
MIN_IBEAM_WIDTH_MM = 40
MIN_IBEAM_WEB_THICKNESS_MM = config.MIN_IBEAM_WEB_THICKNESS_MM # (from env config)
MIN_IBEAM_FLANGE_THICKNESS_MM = 5.0

# --- Geometry Ratios ---
# Web thickness should be at least 1/50th of depth
MIN_WEB_TO_DEPTH_RATIO = 0.02

# Flange width should be at least 1/4th of depth
MIN_WIDTH_TO_DEPTH_RATIO = 0.25

# Flange thickness should be at most 1/10th of flange width
MAX_FLANGE_THICKNESS_TO_WIDTH_RATIO = 0.20

# Web thickness should be at most 1/5th of flange width
MAX_WEB_THICKNESS_TO_WIDTH_RATIO = 0.25

# --- Column Limits ---
MAX_COLUMN_WIDTH_MM = 1500      # Maximum column width for stability
MAX_COLUMN_HEIGHT_MM = 3000     # Maximum column height for manufacturing
MIN_COLUMN_WIDTH_MM = 100       # Minimum column width for structural integrity
MIN_COLUMN_HEIGHT_MM = 200      # Minimum column height for structural integrity
MAX_COLUMN_ASPECT_RATIO = 3.0   # Height/width ratio limit (prevents overly tall/thin columns)
MIN_COLUMN_ASPECT_RATIO = 0.33  # Width/height ratio limit (prevents overly wide/short columns)
