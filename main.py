"""
Main Entry Point.

Entry point script to run the DXF Generator CLI.
"""
import sys
import os

# Add the current directory to python path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dxf_generator.interface.cli import run_cli

if __name__ == "__main__":
    run_cli()
