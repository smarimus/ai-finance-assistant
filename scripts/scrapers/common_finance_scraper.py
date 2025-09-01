#!/usr/bin/env python3
"""
Quick scraper for additional widely-used financial topics
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CommonFinanceTopicsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.output_dir = Path(__file__).parent.parent.parent / "src/data/knowledge_base"
        
        # Common financial topics people search for
        self.common_topics = [
            "https://www.investopedia.com/terms/c/creditreport.asp",
            "https://www.investopedia.com/terms/c/credit_score.asp", 
            "https://www.investopedia.com/terms/e/emergency_fund.asp",
            "https://www.investopedia.com/terms/b/budget.asp",
            "https://www.investopedia.com/terms/c/compound-interest.asp",
            "https://www.investopedia.com/terms/h/homeowners-insurance.asp",
            "https://www.investopedia.com/terms/h/health_insurance.asp",
            "https://www.investopedia.com/terms/l/lifeinsurance.asp",
            "https://www.investopedia.com/terms/m/mortgage.asp",
            "https://www.investopedia.com/terms/s/student-loan.asp",
        ]

    def clean_text(self, text):
        return ' '.join(text.split()) if text else ""

    def scrape_article(self, url):
        try:
            logging.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = self.clean_text(title_elem.get_text()) if title_elem else "Unknown Title"
            
            # Extract content
            content_selectors = [
                '[data-module="ArticleBody"]',
                '.article-body', 
                'article'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                        unwanted.decompose()
                    
                    paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4', 'li'])
                    content_parts = [self.clean_text(p.get_text()) for p in paragraphs if self.clean_text(p.get_text())]
                    content = ' '.join(content_parts)
                    break
            
            if not content or len(content) < 500:
                logging.warning(f"Insufficient content for {url}")
                return None
                
            article_data = {
                'title': title,
                'url': url,
                'content': content,
                'word_count': len(content.split()),
                'source': 'Investopedia',
                'category': 'personal_finance',
                'scraped_at': datetime.now().isoformat(),
                'author': None
            }
            
            logging.info(f"✓ Scraped: {title} ({article_data['word_count']} words)")
            return article_data
            
        except Exception as e:
            logging.error(f"✗ Failed to scrape {url}: {e}")
            return None

    def scrape_common_topics(self):
        articles = []
        
        for i, url in enumerate(self.common_topics, 1):
            logging.info(f"Processing {i}/{len(self.common_topics)}: {url}")
            
            article = self.scrape_article(url)
            if article:
                articles.append(article)
                
                # Save individual article
                filename = f"finance_{i:03d}_{article['title'][:50].replace(' ', '_').replace('/', '_')}.json"
                filename = "".join(c for c in filename if c.isalnum() or c in '._-')
                
                article_path = self.output_dir / "articles" / filename
                article_path.parent.mkdir(exist_ok=True)
                
                with open(article_path, 'w', encoding='utf-8') as f:
                    json.dump(article, f, indent=2, ensure_ascii=False)
                    
            time.sleep(2)  # Be respectful
                
        return articles

def main():
    print("🚀 Scraping Common Personal Finance Topics")
    print("=" * 45)
    
    scraper = CommonFinanceTopicsScraper()
    articles = scraper.scrape_common_topics()
    
    print(f"\\n✅ Scraped {len(articles)} additional finance articles")
    print(f"Total words: {sum(a['word_count'] for a in articles):,}")
    
    for i, article in enumerate(articles, 1):
        print(f"  {i:2d}. {article['title']} ({article['word_count']} words)")

if __name__ == "__main__":
    main()
