import uvicorn
import os
import sys
from dxf_generator.config.env_config import config

# Add the current directory to python path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Ensure the cache directory exists to avoid ezdxf warnings
    cache_dir = os.path.expanduser("~/.cache/ezdxf")
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except Exception:
        pass

    uvicorn.run(
        "dxf_generator.interface.web:app", 
        host=config.API_HOST, 
        port=config.API_PORT, 
        reload=config.API_RELOAD, 
        workers=config.API_WORKERS
    )
