import pytest
import sys
import os

if __name__ == "__main__":
    # Ensure the current directory is in PYTHONPATH so imports work correctly
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Run pytest and exit with the return code
    # We use -v for verbose output and -p no:warnings to keep it clean if needed
    # but let's keep it simple and effective
    sys.exit(pytest.main(["-v", "tests"]))
