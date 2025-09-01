# Scrapers Directory

This directory contains various financial content scrapers for building the knowledge base.

## 📁 Current Scrapers

### 🎯 Main Scrapers (Active)
- **`run_scraper.py`** - Main financial scraper (renamed from investing scraper)
- **`test_scraper.py`** - Test main scraper functionality

### 🔍 Specialized Scrapers (Reference)
- **`retirement_scraper.py`** - Specialized retirement planning content scraper
  - Focuses on 401k, IRA, Social Security topics
  - Sources from Investopedia retirement sections
  - 15 retirement-specific URLs
  
- **`common_finance_scraper.py`** - Personal finance topics scraper
  - Credit scores, budgeting, insurance, mortgages
  - Common financial literacy topics
  - 10 essential personal finance URLs

### 📚 Historical Scrapers (Archive)
- **`run_investing_scraper.py`** - Original Investing.com scraper
- **`test_investing_scraper.py`** - Original test script

## 🚀 Usage

### Main Scraper (Recommended)
```bash
# From project root
python main.py scrape [--max-articles N]

# Or directly
python scripts/scrapers/run_scraper.py
```

### Specialized Scrapers
```bash
# Retirement planning content
python scripts/scrapers/retirement_scraper.py

# Personal finance basics
python scripts/scrapers/common_finance_scraper.py

# Original investing scraper
python scripts/scrapers/run_investing_scraper.py
```

## 📊 Content Coverage

### Current Knowledge Base (41 articles, 77K+ words)
- **🏦 Retirement Planning** (7 articles): 401k, IRA, Social Security
- **💰 Personal Finance** (8 articles): Credit, budgeting, insurance
- **📈 Investment Analysis** (26 articles): Stocks, crypto, financial ratios

### Sources Used
1. **Investing.com Academy** - Main source for investment education
2. **Investopedia** - Retirement and personal finance definitions
3. **Multiple Categories** - Education, retirement_planning, personal_finance

## 🛠️ Scraper Architecture

All scrapers follow this pattern:
```python
class ScrapeClass:
    def __init__(self, delay=1.5, max_retries=3)
    def discover_urls(self) -> List[str]
    def scrape_article(self, url: str) -> Dict
    def scrape_knowledge_base(self, max_articles=None) -> List[Dict]
```

### Common Features
- Rate limiting with configurable delays
- Retry logic for failed requests
- Content validation (minimum word count)
- Structured JSON output
- Progress tracking and logging
- Metadata extraction (title, category, word count)

## 📝 Output Format

All scrapers produce articles in this format:
```json
{
    "title": "Article Title",
    "url": "https://source.com/article",
    "content": "Full article text...",
    "category": "education|retirement_planning|personal_finance",
    "word_count": 1500,
    "source": "Investing.com|Investopedia",
    "scraped_at": "2025-08-13T23:17:36",
    "author": "Author Name"
}
```

## 🎯 Best Practices

### When to Use Each Scraper

1. **`run_scraper.py`** (Main)
   - General financial education content
   - Building comprehensive knowledge base
   - Regular content updates

2. **`retirement_scraper.py`**
   - Need more retirement planning content
   - 401k/IRA specific information
   - Supplementing main knowledge base

3. **`common_finance_scraper.py`**
   - Personal finance basics
   - Credit and budgeting topics
   - Financial literacy content

### Expansion Strategy
```bash
# Step 1: Run main scraper for broad coverage
python main.py scrape --max-articles 50

# Step 2: Add specialized content
python scripts/scrapers/retirement_scraper.py

# Step 3: Fill gaps with personal finance
python scripts/scrapers/common_finance_scraper.py

# Step 4: Rebuild vector database
python main.py build-db
```

## ⚙️ Configuration

### Rate Limiting
- Default: 1.5-2 seconds between requests
- Adjust in scraper `__init__()` method
- Respect website rate limits

### Content Quality
- Minimum content length: 500 characters
- Automatic content cleaning
- Duplicate detection by URL

### Error Handling
- Retry failed requests (3x default)
- Skip invalid articles gracefully
- Continue scraping on individual failures

## 🚀 Future Scrapers

Potential additions:
- **Tax planning scraper** - Tax strategies and planning
- **Real estate scraper** - Property investment content
- **Business finance scraper** - Small business financial content
- **International finance scraper** - Global investment topics

## 📖 Integration

After running any scraper:
```bash
# Check what was scraped
python main.py progress

# Rebuild vector database with new content
python main.py build-db

# Test the updated system
python main.py test-db
```

## 🔧 Troubleshooting

### Common Issues
1. **Rate limiting (429 errors)**: Increase delay between requests
2. **Content not found**: Check URL patterns and selectors
3. **Low quality content**: Adjust minimum content length
4. **Import errors**: Ensure scripts run from project root

### Debug Mode
Most scrapers support verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
