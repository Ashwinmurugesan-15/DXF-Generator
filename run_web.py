import uvicorn
import os
import sys

# Add the current directory to python path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run("dxf_generator.interface.web:app", host="0.0.0.0", port=8000, reload=True)
