#!/usr/bin/env python3
"""
Quick script to scrape Investing.com knowledge base
Run this to start scraping financial content from Investing.com
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import modules
sys.path.append(str(Path(__file__).parent / "src"))

from data.investing_scraper import InvestingKnowledgeBaseScraper


def run_scraper(max_articles=None):
    """Run the Investing.com scraper with optional article limit."""
    print("🚀 Starting Investing.com Knowledge Base Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = InvestingKnowledgeBaseScraper(
        delay_between_requests=1.5,  # Reasonable delay
        max_retries=3
    )
    
    try:
        # Start scraping
        articles = scraper.scrape_knowledge_base(max_articles=max_articles)
        
        print(f"\n✅ SUCCESS!")
        print(f"Scraped {len(articles)} articles")
        print(f"Total words: {sum(a.word_count for a in articles):,}")
        print(f"Data saved to: {scraper.output_dir}")
        
        return articles
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        return []
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return []


if __name__ == "__main__":
    # You can modify this number to control how many articles to scrape
    # Set to None to scrape all available articles
    MAX_ARTICLES = 30  # Start with 30 articles for testing
    
    print(f"📊 Will scrape up to {MAX_ARTICLES} articles from Investing.com")
    print("⏱️  This may take several minutes...")
    print("🔄 Progress will be shown as we go\n")
    
    articles = run_scraper(max_articles=MAX_ARTICLES)
    
    if articles:
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📁 Check the 'src/data/knowledge_base' folder for your data")
    else:
        print(f"\n⚠️  No articles were scraped")
