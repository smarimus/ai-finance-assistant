# Financial Knowledge Base Scraper

This tool scrapes high-quality financial educational content from professional financial websites to build a comprehensive knowledge base for AI finance assistants.

## Features

- **Professional Content Sources**: Currently sources from Investing.com Academy with 128+ educational articles
- **Comprehensive Coverage**: Covers stocks, crypto, forex, commodities, financial analysis, and trading
- **High-Quality Content**: Includes detailed explanations, formulas, examples, and practical applications
- **Respectful Scraping**: Built-in delays and retry logic to respect server resources
- **Content Cleaning**: Automatically cleans and processes extracted content
- **Structured Storage**: Saves articles as JSON files with comprehensive metadata

## Current Content Sources

### Investing.com Academy ✅
- **Stocks Education**: Market basics, order types, analysis techniques
- **Cryptocurrency**: Bitcoin, altcoins, ICOs, trading strategies  
- **Financial Analysis**: Ratios, metrics, valuation methods
- **Trading**: Technical analysis, fundamental analysis, risk management
- **Investment Strategy**: Portfolio management, sector analysis

## Quick Start

### 1. Test the Scraper

```bash
python test_scraper.py
```

### 2. Start Scraping

```bash
python run_scraper.py
```

### 3. Check Progress

```bash
python check_progress.py
```

## Output Structure

```
src/data/knowledge_base/
├── articles/
│   ├── investing_article_0001.json
│   ├── investing_article_0002.json
│   └── ... (25+ articles)
└── investing_scraping_summary.json
```

Each article includes:
```json
{
  "url": "source_url",
  "title": "Article Title", 
  "content": "Full content text...",
  "category": "education|analysis|news",
  "tags": ["relevant", "keywords"],
  "published_date": "date_if_available",
  "author": "author_if_available",
  "word_count": 1500,
  "scraped_at": "2025-08-13 23:07:18"
}
```

## Current Knowledge Base Stats

✅ **25 High-Quality Articles**  
✅ **39,218+ Words** of professional content  
✅ **128 URLs Discovered** (more content available)  
✅ **83% Success Rate** in content extraction

## Sample Content Topics

- **ICO Guide** (3,538 words) - Comprehensive cryptocurrency education
- **Magnificent 7 Stocks** (2,424 words) - Major tech stock analysis
- **Capital Expenditures** (2,105 words) - Financial analysis fundamentals
- **Cryptocurrency Basics** (2,237 words) - Digital asset education
- **Working Capital Analysis** (1,668 words) - Business finance
- **Interest Coverage Ratios** (1,940 words) - Financial metrics
- **Stock Order Types** (1,323 words) - Trading fundamentals
- **Sloan Ratio Analysis** (1,283 words) - Earnings quality assessment

## Configuration

Customize scraping in `run_scraper.py`:

```python
# Number of articles to scrape (None = all available)
MAX_ARTICLES = 50  

# Scraper settings
scraper = InvestingKnowledgeBaseScraper(
    delay_between_requests=1.5,  # Respectful delay
    max_retries=3               # Error recovery
)
```

## Files Overview

- `src/data/financial_scraper.py` - Main scraper implementation
- `run_scraper.py` - Easy-to-use script to start scraping
- `test_scraper.py` - Verify scraper functionality 
- `check_progress.py` - Monitor scraping progress
- `src/data/knowledge_base/` - Scraped content storage

## Usage in Your Application

```python
from src.data.financial_scraper import InvestingKnowledgeBaseScraper

# Initialize and run scraper
scraper = InvestingKnowledgeBaseScraper()
articles = scraper.scrape_knowledge_base(max_articles=10)

# Process results
for article in articles:
    print(f"Title: {article.title}")
    print(f"Content: {article.content[:200]}...")
```

## Why This Knowledge Base is Valuable

🎯 **Professional Quality**: Content from established financial education platforms  
📚 **Comprehensive Coverage**: Broad range of financial topics and concepts  
💰 **Practical Focus**: Real-world applications and examples  
🔍 **Detailed Analysis**: In-depth explanations with formulas and calculations  
📊 **Current Information**: Up-to-date financial concepts and practices  
🛠️ **AI-Ready Format**: Clean, structured JSON perfect for AI training  

## Expanding the Knowledge Base

The scraper architecture supports adding new sources:

1. **Additional Educational Platforms**: Can be extended to other financial education sites
2. **Specialized Content**: Target specific areas like options trading, forex, etc.
3. **Multi-Language Support**: Extend to non-English financial content
4. **Regular Updates**: Schedule periodic scraping for fresh content

## Legal and Ethical Considerations

- Content scraped for educational/research purposes
- Respectful scraping with appropriate delays
- Source attribution maintained in metadata
- Consider terms of service for commercial use
