import os
from typing import List
from dxf_generator.config.logging_config import logger

def remove_file(path: str):
    """Helper to remove file after response is sent."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Error removing temporary file {path}: {e}")

def remove_files(paths: List[str]):
    """Helper to remove multiple files."""
    for path in paths:
        remove_file(path)

