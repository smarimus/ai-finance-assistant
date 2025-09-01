#!/usr/bin/env python3
"""
Specialized scraper for retirement planning and 401k content
Focuses on personal finance and retirement topics
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RetirementKnowledgeScraper:
    def __init__(self, delay_between_requests=2.0, max_retries=3):
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.output_dir = Path(__file__).parent.parent.parent / "src/data/knowledge_base"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Retirement-focused URLs to scrape
        self.retirement_urls = [
            # General retirement planning
            "https://www.investopedia.com/retirement/401k-plans/",
            "https://www.investopedia.com/terms/1/401kplan.asp",
            "https://www.investopedia.com/retirement/roth-vs-traditional-ira-which-is-right-for-you/",
            "https://www.investopedia.com/terms/i/ira.asp",
            "https://www.investopedia.com/retirement/how-much-you-need-to-save-for-retirement/",
            "https://www.investopedia.com/articles/personal-finance/040315/401k-403b-457-retirement-plans-compared.asp",
            "https://www.investopedia.com/terms/r/roth-ira.asp",
            "https://www.investopedia.com/retirement/pension-plans/",
            "https://www.investopedia.com/terms/t/traditionalira.asp",
            "https://www.investopedia.com/retirement/how-plan-retirement/",
            "https://www.investopedia.com/terms/s/sep.asp",
            "https://www.investopedia.com/terms/s/simple-ira.asp",
            "https://www.investopedia.com/retirement/when-should-you-start-taking-social-security/",
            "https://www.investopedia.com/terms/s/socialsecurity.asp",
            "https://www.investopedia.com/retirement/how-to-catch-up-retirement-savings/",
        ]

    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        return ' '.join(text.split())

    def scrape_investopedia_article(self, url):
        """Scrape a single article from Investopedia."""
        try:
            logging.info(f"Scraping: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = self.clean_text(title_elem.get_text()) if title_elem else "Unknown Title"
            
            # Extract main content
            content_selectors = [
                '[data-module="ArticleBody"]',
                '.article-body',
                '.comp.mntl-sc-page.mntl-block article',
                'article',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'aside', '.ad']):
                        unwanted.decompose()
                    
                    # Get text content
                    paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4', 'li'])
                    content_parts = [self.clean_text(p.get_text()) for p in paragraphs if self.clean_text(p.get_text())]
                    content = ' '.join(content_parts)
                    break
            
            if not content or len(content) < 500:
                logging.warning(f"Insufficient content for {url}")
                return None
                
            # Create article data
            article_data = {
                'title': title,
                'url': url,
                'content': content,
                'word_count': len(content.split()),
                'source': 'Investopedia',
                'category': 'retirement_planning',
                'scraped_at': datetime.now().isoformat(),
                'author': None
            }
            
            logging.info(f"✓ Scraped: {title} ({article_data['word_count']} words)")
            return article_data
            
        except Exception as e:
            logging.error(f"✗ Failed to scrape {url}: {e}")
            return None

    def scrape_retirement_knowledge(self, max_articles=None):
        """Scrape retirement planning articles."""
        logging.info("Starting retirement planning knowledge base scraping...")
        
        urls_to_process = self.retirement_urls[:max_articles] if max_articles else self.retirement_urls
        articles = []
        
        for i, url in enumerate(urls_to_process, 1):
            logging.info(f"Processing {i}/{len(urls_to_process)}: {url}")
            
            article = self.scrape_investopedia_article(url)
            if article:
                articles.append(article)
                
                # Save individual article
                filename = f"retirement_{i:03d}_{article['title'][:50].replace(' ', '_').replace('/', '_')}.json"
                filename = "".join(c for c in filename if c.isalnum() or c in '._-')
                
                article_path = self.output_dir / "articles" / filename
                article_path.parent.mkdir(exist_ok=True)
                
                with open(article_path, 'w', encoding='utf-8') as f:
                    json.dump(article, f, indent=2, ensure_ascii=False)
                    
            # Delay between requests
            if i < len(urls_to_process):
                time.sleep(self.delay)
                
        # Save summary
        if articles:
            summary = {
                'source': 'Multiple (Retirement Focus)',
                'total_articles': len(articles),
                'total_words': sum(a['word_count'] for a in articles),
                'urls_processed': len(urls_to_process),
                'successful_scrapes': len(articles),
                'scraping_date': datetime.now().isoformat(),
                'categories': {'retirement_planning': len(articles)}
            }
            
            summary_path = self.output_dir / "retirement_scraping_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Saved {len(articles)} retirement articles")
            logging.info(f"Summary saved to {summary_path}")
            
        return articles


def main():
    """Run the retirement knowledge scraper."""
    print("🚀 Starting Retirement Planning Knowledge Scraper")
    print("=" * 55)
    
    scraper = RetirementKnowledgeScraper(delay_between_requests=2.0)
    
    try:
        articles = scraper.scrape_retirement_knowledge(max_articles=15)
        
        print(f"\n✅ SUCCESS!")
        print(f"Scraped {len(articles)} retirement planning articles")
        print(f"Total words: {sum(a['word_count'] for a in articles):,}")
        print(f"Data saved to: {scraper.output_dir}")
        
        # Show what we got
        if articles:
            print(f"\n📚 Articles scraped:")
            for i, article in enumerate(articles, 1):
                print(f"  {i:2d}. {article['title']} ({article['word_count']} words)")
        
        return articles
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        return []
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return []


if __name__ == "__main__":
    main()
