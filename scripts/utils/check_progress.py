#!/usr/bin/env python3
"""
Check the progress and results of the Zerodha scraper
"""

import json
from pathlib import Path


def check_scraper_progress():
    """Check the current state of scraped data."""
    base_dir = Path(__file__).parent.parent.parent / "src/data/knowledge_base"
    
    if not base_dir.exists():
        print("❌ Knowledge base directory doesn't exist yet")
        return
    
    articles_dir = base_dir / "articles"
    summary_files = [
        base_dir / "scraping_summary.json",
        base_dir / "investing_scraping_summary.json"
    ]
    
    # Check for articles
    if articles_dir.exists():
        articles = list(articles_dir.glob("*.json"))
        print(f"📄 Found {len(articles)} scraped articles")
        
        if articles:
            # Show a sample article
            with open(articles[0], 'r') as f:
                sample = json.load(f)
            print(f"\n📝 Sample article:")
            print(f"   Title: {sample['title']}")
            print(f"   URL: {sample['url']}")
            print(f"   Words: {sample['word_count']}")
            print(f"   Category: {sample['category']}")
            if 'author' in sample:
                print(f"   Author: {sample.get('author', 'N/A')}")
            print(f"   Content preview: {sample['content'][:200]}...")
    else:
        print("📄 No articles directory found yet")
    
    # Check for summary files
    summary_found = False
    for summary_file in summary_files:
        if summary_file.exists():
            summary_found = True
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            print(f"\n📊 Scraping Summary ({summary_file.name}):")
            print(f"   Source: {summary.get('source', 'Unknown')}")
            print(f"   Total articles: {summary['total_articles']}")
            print(f"   Total words: {summary['total_words']:,}")
            print(f"   URLs processed: {summary['urls_processed']}")
            print(f"   Scraping date: {summary['scraping_date']}")
            
            print(f"\n📂 Categories:")
            for category, stats in summary['categories'].items():
                print(f"   {category}: {stats['count']} articles ({stats['words']:,} words)")
            break
    
    if not summary_found:
        print("📊 No summary file found yet")


if __name__ == "__main__":
    print("🔍 Checking scraper progress...\n")
    check_scraper_progress()
