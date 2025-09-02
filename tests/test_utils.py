#!/usr/bin/env python3
"""
Test utilities for setting up import paths
"""

import sys
import os
from pathlib import Path

def setup_test_path():
    """Add the project root to sys.path so we can import from src"""
    # Get the project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent
    src_path = str(project_root)
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    return project_root
