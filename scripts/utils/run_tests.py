#!/usr/bin/env python3
"""
Test runner script for AI Finance Assistant

Usage:
    python run_tests.py [test_category]

Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py agents            # Run only agent tests
    python run_tests.py utils             # Run only utility tests
    python run_tests.py integration       # Run only integration tests
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests(test_category=None):
    """Run tests with optional category filter"""
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    os.environ["PYTHONPATH"] = str(src_path)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest", "-v"]
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    except ImportError:
        print("Coverage not available. Install with: pip install coverage pytest-cov")
    
    # Determine test path based on category
    if test_category == "agents":
        cmd.append("tests/test_agents/")
    elif test_category == "core":
        cmd.append("tests/test_core/")
    elif test_category == "utils":
        cmd.append("tests/test_utils/")
    elif test_category == "rag":
        cmd.append("tests/test_rag/")
    elif test_category == "data":
        cmd.append("tests/test_data/")
    elif test_category == "integration":
        cmd.extend(["-m", "integration"])
    elif test_category is None:
        cmd.append("tests/")
    else:
        print(f"Unknown test category: {test_category}")
        print("Available categories: agents, core, utils, rag, data, integration")
        return 1
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install with: pip install pytest")
        return 1

def check_test_dependencies():
    """Check if required test dependencies are installed"""
    required_packages = ["pytest"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing test dependencies:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    
    return True

if __name__ == "__main__":
    # Check dependencies first
    if not check_test_dependencies():
        sys.exit(1)
    
    # Get test category from command line
    test_category = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run tests
    exit_code = run_tests(test_category)
    sys.exit(exit_code)
