#!/usr/bin/env python3
"""
Test Runner for AI Finance Assistant
Organized test execution with different test categories
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_tests(test_type="all", verbose=False):
    """Run tests based on category"""
    
    base_cmd = ["python", "-m", "pytest"]
    if verbose:
        base_cmd.extend(["-v", "--tb=short"])
    
    test_commands = {
        "unit": base_cmd + ["tests/test_agents/", "tests/test_core/", "tests/test_utils/"],
        "integration": base_cmd + ["tests/integration/"],
        "phase": base_cmd + ["tests/phase_tests/"],
        "performance": base_cmd + ["tests/performance/"],
        "all": base_cmd + ["tests/"],
    }
    
    if test_type not in test_commands:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_commands.keys())}")
        return False
    
    print(f"🧪 Running {test_type} tests...")
    try:
        result = subprocess.run(test_commands[test_type], check=True)
        print(f"✅ {test_type.title()} tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {test_type.title()} tests failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run AI Finance Assistant tests")
    parser.add_argument(
        "test_type", 
        nargs="?", 
        default="all",
        choices=["unit", "integration", "phase", "performance", "all"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("🏦 AI Finance Assistant Test Runner")
    print("=" * 40)
    
    success = run_tests(args.test_type, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
