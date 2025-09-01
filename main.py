#!/usr/bin/env python3
"""
AI Finance Assistant - Main Entry Point
Organized script launcher for all project functionality
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_script(script_path: str, args: list = None):
    """Run a script with optional arguments"""
    if args is None:
        args = []
    
    script_full_path = Path(__file__).parent / script_path
    cmd = [sys.executable, str(script_full_path)] + args
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def show_help():
    """Show available commands"""
    print("""
🚀 AI Finance Assistant - Project Scripts
=========================================

📚 KNOWLEDGE BASE SCRAPING:
  python main.py scrape [--max-articles N]     - Run financial content scraper
  python main.py scrape-retirement             - Run retirement planning scraper
  python main.py scrape-personal               - Run personal finance scraper
  python main.py test-scraper                  - Test scraper functionality
  python main.py progress                      - Check scraping progress

🔍 VECTOR DATABASE:
  python main.py build-db [--embedding-model MODEL] - Build FAISS vector database  
  python main.py test-db                       - Test vector database functionality
  python main.py db-examples                   - Interactive vector database examples
  python main.py setup-db                      - Vector database setup guide

🛠️  UTILITIES:
  python main.py test                          - Run all tests
  python main.py help                          - Show this help

📁 DIRECT SCRIPT ACCESS:
  scripts/scrapers/run_scraper.py             - Main scraper
  scripts/vector_db/build_vector_db.py        - Vector database builder
  scripts/utils/check_progress.py             - Progress checker

🎯 QUICK START:
  1. python main.py scrape                    - Build knowledge base
  2. python main.py build-db                  - Create vector database
  3. python main.py test-db                   - Test everything

📖 For detailed help on any command:
  python main.py COMMAND --help
""")

def main():
    """Main entry point with command routing"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    remaining_args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Command routing
    if command == "scrape":
        print("🚀 Running Financial Knowledge Base Scraper...")
        run_script("scripts/scrapers/run_scraper.py", remaining_args)
        
    elif command == "scrape-retirement":
        print("🏦 Running Retirement Planning Scraper...")
        run_script("scripts/scrapers/retirement_scraper.py", remaining_args)
        
    elif command == "scrape-personal":
        print("💰 Running Personal Finance Scraper...")
        run_script("scripts/scrapers/common_finance_scraper.py", remaining_args)
        
    elif command == "test-scraper":
        print("🧪 Testing Scraper Functionality...")
        run_script("scripts/scrapers/test_scraper.py", remaining_args)
        
    elif command == "progress":
        print("📊 Checking Scraper Progress...")
        run_script("scripts/utils/check_progress.py", remaining_args)
        
    elif command == "build-db":
        print("🔍 Building FAISS Vector Database...")
        run_script("scripts/vector_db/build_vector_db.py", remaining_args)
        
    elif command == "test-db":
        print("🧪 Testing Vector Database...")
        run_script("scripts/vector_db/test_vector_db.py", remaining_args)
        
    elif command == "db-examples":
        print("💡 Running Vector Database Examples...")
        run_script("scripts/vector_db/vector_db_examples.py", remaining_args)
        
    elif command == "setup-db":
        print("📖 Vector Database Setup Guide...")
        run_script("scripts/vector_db/setup_vector_db.py", remaining_args)
        
    elif command == "test":
        print("🧪 Running All Tests...")
        run_script("scripts/utils/run_tests.py", remaining_args)
        
    elif command in ["help", "-h", "--help"]:
        show_help()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run 'python main.py help' for available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()
