#!/usr/bin/env python3
"""
UHFF Visualization Entry Point for Android

This module serves as the main entry point for the Android APK build.
It imports and runs the main visualization application with Android optimizations.
"""

import os
import sys

# Add the current directory to the Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from main import main
    
    # Run the main application
    if __name__ == "__main__":
        print("Starting UHFF Visualization for Android...")
        main()
        
except ImportError as e:
    print(f"Error importing main module: {e}")
    print("Make sure main.py is in the same directory as this file.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
