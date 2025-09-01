#!/usr/bin/env python3
"""
Test script to verify the financial knowledge base scraper is working correctly
"""

import sys
from pathlib import Path

# Add src to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from data.financial_scraper import InvestingKnowledgeBaseScraper


def test_investing_scraper():
    """Test the financial knowledge base scraper with a few URLs."""
    print("🧪 Testing Financial Knowledge Base Scraper...")
    
    # Initialize scraper
    scraper = InvestingKnowledgeBaseScraper()
    
    # Test sitemap URL fetching
    print("📊 Fetching sitemap URLs...")
    try:
        urls = scraper.get_sitemap_urls()
        print(f"✅ Found {len(urls)} knowledge URLs")
        
        if urls:
            print(f"📝 Sample URLs:")
            for i, url in enumerate(urls[:10]):  # Show first 10
                print(f"  {i+1}. {url}")
        
        # Test scraping a single article
        if urls:
            print(f"\n🔍 Testing article scraping with first URL...")
            test_url = urls[0]
            article = scraper.scrape_article(test_url)
            
            if article:
                print(f"✅ Successfully scraped article:")
                print(f"   Title: {article.title}")
                print(f"   Category: {article.category}")
                print(f"   Word count: {article.word_count}")
                print(f"   Author: {article.author}")
                print(f"   Published: {article.published_date}")
                print(f"   Tags: {article.tags[:3] if article.tags else 'None'}")
                print(f"   Content preview: {article.content[:300]}...")
                return True
            else:
                print(f"❌ Failed to scrape test article")
                return False
        else:
            print("❌ No URLs found to test")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_url():
    """Test with a known Investing.com educational URL."""
    print("\n🎯 Testing with specific educational URL...")
    
    scraper = InvestingKnowledgeBaseScraper()
    
    # Test with a known educational article
    test_urls = [
        "https://www.investing.com/academy/forex/what-is-forex/",
        "https://www.investing.com/academy/stocks/what-are-stocks/",
        "https://www.investing.com/analysis/"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        article = scraper.scrape_article(url)
        
        if article:
            print(f"✅ Success: {article.title} ({article.word_count} words)")
            return True
        else:
            print(f"❌ Failed to scrape: {url}")
    
    return False


if __name__ == "__main__":
    print("🔬 Running financial scraper tests...\n")
    
    # Test sitemap discovery
    success1 = test_investing_scraper()
    
    # Test specific URLs
    success2 = test_specific_url()
    
    if success1 or success2:
        print(f"\n🎉 Test passed! The financial scraper is ready to use.")
        print(f"🚀 Run 'python run_scraper.py' to start full scraping.")
    else:
        print(f"\n⚠️  Tests failed. The scraper may need adjustments.")
        print(f"💡 Try checking the URLs manually in a browser first.")
