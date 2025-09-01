# Scripts Directory

This directory contains all the organized scripts for the AI Finance Assistant project.

## 📁 Directory Structure

```
scripts/
├── scrapers/           # Knowledge base scraping scripts
│   ├── run_scraper.py     # Main scraper for financial content
│   └── test_scraper.py    # Test scraper functionality
├── vector_db/          # FAISS vector database scripts  
│   ├── build_vector_db.py    # Build FAISS vector database
│   ├── test_vector_db.py     # Test vector database
│   ├── vector_db_examples.py # Interactive examples
│   └── setup_vector_db.py    # Setup guide
└── utils/              # Utility and testing scripts
    ├── check_progress.py     # Check scraping progress
    ├── run_tests.py         # Run all tests
    └── test_setup.py        # Test environment setup
```

## 🚀 How to Use

### Option 1: Use Main Entry Point (Recommended)
```bash
# From project root directory
python main.py scrape           # Run scraper
python main.py build-db         # Build vector database
python main.py test-db          # Test vector database
python main.py help             # Show all commands
```

### Option 2: Run Scripts Directly
```bash
# From project root directory
python scripts/scrapers/run_scraper.py
python scripts/vector_db/build_vector_db.py
python scripts/utils/check_progress.py
```

### Option 3: Use Convenience Scripts
```bash
# From project root directory
python run_scraper.py          # Points to scripts/scrapers/run_scraper.py
python build_vector_db.py      # Points to scripts/vector_db/build_vector_db.py
python check_progress.py       # Points to scripts/utils/check_progress.py
```

## 📚 Script Categories

### 🔍 Scrapers (`scripts/scrapers/`)
- **`run_scraper.py`**: Main script to scrape financial knowledge base
- **`test_scraper.py`**: Test and validate scraper functionality
- **`retirement_scraper.py`**: Specialized retirement planning content (401k, IRA, Social Security)
- **`common_finance_scraper.py`**: Personal finance basics (credit, budgeting, insurance)
- **`run_investing_scraper.py`**: Original Investing.com scraper (archive)
- **`test_investing_scraper.py`**: Original test script (archive)

### 🔍 Vector Database (`scripts/vector_db/`)
- **`build_vector_db.py`**: Build FAISS vector database from knowledge base
- **`test_vector_db.py`**: Comprehensive testing of vector database
- **`vector_db_examples.py`**: Interactive examples and demos
- **`setup_vector_db.py`**: Complete setup guide with requirements check

### 🛠️ Utilities (`scripts/utils/`)
- **`check_progress.py`**: Monitor scraping progress and statistics
- **`run_tests.py`**: Run complete test suite
- **`test_setup.py`**: Test environment setup and dependencies

## 🎯 Common Workflows

### 1. Initial Setup
```bash
python main.py scrape           # Build knowledge base (77K+ words)
python main.py build-db         # Create vector database
python main.py test-db          # Verify everything works
```

### 2. Development Workflow
```bash
python main.py progress         # Check current data
python main.py test             # Run all tests
python main.py db-examples      # Try interactive features
```

### 3. Expansion Workflow
```bash
python main.py scrape --max-articles 50    # Scrape more content
python main.py build-db                     # Rebuild vector database
python main.py test-db                      # Verify new data
```

## 💡 Path Handling

All scripts are designed to work from the project root directory. They automatically:
- Adjust import paths to find the `src/` directory
- Handle relative file paths correctly
- Work whether called directly or through the main entry point

## 🔧 Environment Variables

Some scripts require environment variables:
- **`OPENAI_API_KEY`**: Required for vector database building (embeddings)

Set it with:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 📖 Getting Help

- Run `python main.py help` for all available commands
- Run any script with `--help` for specific options
- Check the main README.md for project overview
- See VECTOR_DB_GUIDE.md for vector database details

## 🚀 Quick Reference

| Task | Command |
|------|---------|
| Build knowledge base | `python main.py scrape` |
| Create vector database | `python main.py build-db` |
| Test functionality | `python main.py test-db` |
| Check progress | `python main.py progress` |
| Interactive examples | `python main.py db-examples` |
| Run all tests | `python main.py test` |
| Show help | `python main.py help` |
