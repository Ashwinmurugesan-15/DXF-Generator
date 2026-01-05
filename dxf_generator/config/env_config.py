import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    """Centralized configuration management."""
    
    # Server Settings
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_WORKERS = int(os.getenv("API_WORKERS", 4))
    API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"
    
    # Performance Settings
    MAX_THREADS = int(os.getenv("MAX_THREADS", 8))
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", 50))
    
    # System Paths
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    DXF_OUTPUT_DIR = os.getenv("DXF_OUTPUT_DIR", ".")
    
    # Engineering Limits (Allowing environment overrides for existing constants)
    MAX_IBEAM_DEPTH_MM = float(os.getenv("MAX_IBEAM_DEPTH_MM", 1500))
    MIN_IBEAM_WEB_THICKNESS_MM = float(os.getenv("MIN_IBEAM_WEB_THICKNESS_MM", 3.0))

# Create a singleton instance
config = Config()
