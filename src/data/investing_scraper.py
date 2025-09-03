"""
Investing.com Knowledge Base Scraper

This module scrapes financial knowledge content from Investing.com
using their sitemap and BeautifulSoup for content extraction.
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedArticle:
    """Data class for scraped article content."""
    url: str
    title: str
    content: str
    category: str
    tags: List[str]
    published_date: Optional[str] = None
    author: Optional[str] = None
    word_count: int = 0


class InvestingKnowledgeBaseScraper:
    """Scraper for Investing.com's financial knowledge base."""
    
    def __init__(self, 
                 output_dir: str = "src/data/knowledge_base",
                 delay_between_requests: float = 1.5,
                 max_retries: int = 3):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Directory to save scraped content
            delay_between_requests: Delay between HTTP requests
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = "https://www.investing.com"
        self.sitemap_urls = [
            "https://www.investing.com/sitemap.xml",
            "https://www.investing.com/news/sitemap.xml",
            "https://www.investing.com/analysis/sitemap.xml"
        ]
        
        # Educational and analysis sections
        self.educational_sections = [
            "/academy/",
            "/news/",
            "/analysis/",
            "/education/",
            "/tutorial/",
            "/guide/",
            "/basics/",
            "/learn/"
        ]
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Track processed URLs to avoid duplicates
        self.processed_urls: Set[str] = set()
        
        # Financial knowledge categories
        self.target_categories = {
            'academy', 'education', 'tutorial', 'guide', 'basics',
            'analysis', 'news', 'market', 'trading', 'investing',
            'forex', 'crypto', 'stocks', 'commodities', 'etf',
            'bonds', 'economy', 'technical', 'fundamental'
        }
    
    def get_sitemap_urls(self) -> List[str]:
        """Extract URLs from sitemaps and discover educational content."""
        all_urls = []
        
        # Get URLs from sitemaps
        for sitemap_url in self.sitemap_urls:
            try:
                logger.info(f"Fetching sitemap: {sitemap_url}")
                response = self.session.get(sitemap_url, timeout=10)
                response.raise_for_status()
                
                # Parse XML sitemap
                root = ET.fromstring(response.content)
                
                # Handle different namespace possibilities
                namespaces = [
                    {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'},
                    {'ns': 'http://www.google.com/schemas/sitemap/0.9'},
                    {}
                ]
                
                # Extract URLs
                urls_found = 0
                for ns in namespaces:
                    if ns:
                        url_elements = root.findall('.//ns:url', ns)
                        if not url_elements:
                            url_elements = root.findall('.//ns:sitemap', ns)
                    else:
                        url_elements = root.findall('.//url') + root.findall('.//sitemap')
                    
                    for url_elem in url_elements:
                        if ns:
                            loc_elem = url_elem.find('ns:loc', ns)
                        else:
                            loc_elem = url_elem.find('loc')
                        
                        if loc_elem is not None:
                            url = loc_elem.text
                            if self._is_knowledge_url(url):
                                all_urls.append(url)
                                urls_found += 1
                    
                    if urls_found > 0:
                        break
                        
                logger.info(f"Found {urls_found} knowledge URLs in {sitemap_url}")
                
            except Exception as e:
                logger.warning(f"Error fetching sitemap {sitemap_url}: {e}")
                continue
        
        # Discover additional educational content
        educational_urls = self._discover_educational_content()
        all_urls.extend(educational_urls)
        
        # Remove duplicates and sort
        unique_urls = list(set(all_urls))
        logger.info(f"Total unique knowledge URLs found: {len(unique_urls)}")
        return unique_urls
    
    def _discover_educational_content(self) -> List[str]:
        """Discover educational content by exploring known sections."""
        educational_urls = []
        
        logger.info("Discovering educational content sections...")
        
        # Check academy section specifically
        academy_sections = [
            "/academy/forex/",
            "/academy/stocks/", 
            "/academy/crypto/",
            "/academy/commodities/",
            "/academy/analysis/"
        ]
        
        for section in academy_sections:
            try:
                section_url = f"{self.base_url}{section}"
                logger.info(f"Checking section: {section}")
                
                response = self.session.get(section_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article links
                    article_links = soup.find_all('a', href=True)
                    
                    for link in article_links:
                        href = link.get('href')
                        if href:
                            if href.startswith('/'):
                                full_url = f"{self.base_url}{href}"
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            if self._is_knowledge_url(full_url) and full_url not in educational_urls:
                                educational_urls.append(full_url)
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.warning(f"Error discovering section {section}: {e}")
                continue
        
        logger.info(f"Discovered {len(educational_urls)} educational URLs")
        return educational_urls
    
    def _is_knowledge_url(self, url: str) -> bool:
        """Check if URL contains financial knowledge content."""
        if not url or not url.startswith('http'):
            return False
            
        url_lower = url.lower()
        
        # Must be from investing.com
        if 'investing.com' not in url_lower:
            return False
        
        # Include educational and analysis content
        for category in self.target_categories:
            if category in url_lower:
                return True
        
        # Include specific educational paths
        for section in self.educational_sections:
            if section in url_lower:
                return True
        
        # Exclude unwanted pages
        exclude_patterns = [
            'login', 'signup', 'register', 'account', 'admin', 'api',
            'contact', 'support', 'terms', 'privacy', 'cookie',
            'download', 'app', 'mobile', 'portfolio', 'watchlist',
            'calendar', 'rates', 'charts', 'screener', 'tools',
            '/indices/', '/currencies/', '/commodities/', '/etfs/',
            '/rates-bonds/', '/futures/', '/options/', '/stock-screener/'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
                
        return False
    
    def scrape_article(self, url: str) -> Optional[ScrapedArticle]:
        """Scrape content from a single article URL."""
        if url in self.processed_urls:
            return None
            
        try:
            logger.info(f"Scraping: {url}")
            
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")
                        return None
                    
                    # Handle rate limiting
                    if "429" in str(e) or "Too Many Requests" in str(e):
                        wait_time = (2 ** attempt) * 3
                        logger.warning(f"Rate limited, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(2 ** attempt)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup, url)
            if not title:
                logger.warning(f"No title found for {url}")
                return None
            
            # Extract main content
            content = self._extract_content(soup)
            if not content or len(content.strip()) < 100:
                logger.warning(f"Insufficient content for {url}")
                return None
            
            # Extract metadata
            category = self._extract_category(url)
            tags = self._extract_tags(soup)
            published_date = self._extract_date(soup)
            author = self._extract_author(soup)
            
            # Create article object
            article = ScrapedArticle(
                url=url,
                title=title,
                content=content,
                category=category,
                tags=tags,
                published_date=published_date,
                author=author,
                word_count=len(content.split())
            )
            
            self.processed_urls.add(url)
            time.sleep(self.delay)
            
            return article
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract article title."""
        title_selectors = [
            'h1.articleHeader',
            'h1.title',
            'h1',
            '.article-header h1',
            '.post-title',
            '.entry-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 5:
                    return title
        
        # Fallback to meta title
        meta_title = soup.find('meta', attrs={'property': 'og:title'})
        if meta_title:
            return meta_title.get('content', '').strip()
        
        return urlparse(url).path.split('/')[-1].replace('-', ' ').title()
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer',
                           'aside', 'advertisement', 'ad', 'comment', 'sidebar']):
            element.decompose()
        
        # Investing.com specific content selectors
        content_selectors = [
            '.WYSIWYG.articlePage',
            '.articlePage',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'article',
            '.main-content',
            '#article-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    return self._clean_text(text)
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = '\n'.join([p.get_text(strip=True) for p in paragraphs 
                            if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20])
            if len(text) > 200:
                return self._clean_text(text)
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        import re
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Share.*?(?=\n|$)',
            r'Follow.*?(?=\n|$)',
            r'Subscribe.*?(?=\n|$)',
            r'Download.*?(?=\n|$)',
            r'Disclaimer.*?(?=\n|$)',
            r'Risk warning.*?(?=\n|$)'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_category(self, url: str) -> str:
        """Extract category from URL path."""
        path = urlparse(url).path.lower()
        
        if '/academy/' in path:
            return 'education'
        elif '/analysis/' in path:
            return 'analysis'
        elif '/news/' in path:
            return 'news'
        elif any(cat in path for cat in ['forex', 'fx']):
            return 'forex'
        elif any(cat in path for cat in ['crypto', 'bitcoin', 'ethereum']):
            return 'cryptocurrency'
        elif any(cat in path for cat in ['stock', 'equity']):
            return 'stocks'
        elif 'commodit' in path:
            return 'commodities'
        else:
            return 'general'
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags/keywords from the page."""
        tags = []
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            tags.extend([tag.strip() for tag in meta_keywords.get('content', '').split(',')])
        
        # Article tags
        tag_elements = soup.select('.tags a, .tag, .article-tags a, .post-tags a')
        for elem in tag_elements:
            tag_text = elem.get_text().strip()
            if tag_text:
                tags.append(tag_text)
        
        return [tag for tag in tags if tag and len(tag) > 1][:10]  # Limit to 10 tags
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date."""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            '.date',
            '.published',
            '.post-date',
            'time'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.name == 'meta':
                    date_str = date_elem.get('content', '')
                else:
                    date_str = date_elem.get_text().strip()
                
                if date_str:
                    return date_str
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information."""
        author_selectors = [
            'meta[name="author"]',
            '.author',
            '.byline',
            '.post-author',
            '.article-author'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == 'meta':
                    author = author_elem.get('content', '').strip()
                else:
                    author = author_elem.get_text().strip()
                
                if author and len(author) > 1:
                    return author
        
        return None
    
    def save_articles(self, articles: List[ScrapedArticle]) -> None:
        """Save scraped articles to JSON files."""
        if not articles:
            logger.warning("No articles to save")
            return
        
        # Save individual articles
        articles_dir = self.output_dir / "articles"
        articles_dir.mkdir(exist_ok=True)
        
        for i, article in enumerate(articles):
            filename = f"investing_article_{i+1:04d}.json"
            filepath = articles_dir / filename
            
            article_data = {
                'url': article.url,
                'title': article.title,
                'content': article.content,
                'category': article.category,
                'tags': article.tags,
                'published_date': article.published_date,
                'author': article.author,
                'word_count': article.word_count,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_file = self.output_dir / "investing_scraping_summary.json"
        summary = {
            'source': 'Investing.com',
            'total_articles': len(articles),
            'categories': {},
            'total_words': sum(article.word_count for article in articles),
            'urls_processed': len(self.processed_urls),
            'scraping_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Category breakdown
        for article in articles:
            category = article.category
            if category not in summary['categories']:
                summary['categories'][category] = {'count': 0, 'words': 0}
            summary['categories'][category]['count'] += 1
            summary['categories'][category]['words'] += article.word_count
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved {len(articles)} articles to {articles_dir}")
        logger.info(f"Summary saved to {summary_file}")
    
    def scrape_knowledge_base(self, max_articles: Optional[int] = None) -> List[ScrapedArticle]:
        """Main method to scrape the knowledge base."""
        logger.info("Starting Investing.com knowledge base scraping...")
        
        # Get URLs
        urls = self.get_sitemap_urls()
        
        if max_articles:
            urls = urls[:max_articles]
            logger.info(f"Limiting to {max_articles} articles")
        
        articles = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            
            article = self.scrape_article(url)
            if article:
                articles.append(article)
                logger.info(f"✓ Scraped: {article.title} ({article.word_count} words)")
            else:
                logger.warning(f"✗ Failed to scrape: {url}")
            
            # Progress update every 10 articles
            if i % 10 == 0:
                logger.info(f"Progress: {len(articles)}/{i} articles successfully scraped")
        
        # Save all articles
        self.save_articles(articles)
        
        logger.info(f"Scraping completed! {len(articles)} articles saved.")
        return articles


def main():
    """Main function to run the scraper."""
    scraper = InvestingKnowledgeBaseScraper(
        output_dir="/Users/sudhakarmarimuthu/development/py-pro/agents/ai_finance_assistant/src/data/knowledge_base",
        delay_between_requests=1.5,
        max_retries=3
    )
    
    # Scrape knowledge base
    articles = scraper.scrape_knowledge_base(max_articles=50)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"INVESTING.COM SCRAPING SUMMARY")
    print(f"{'='*50}")
    print(f"Total articles scraped: {len(articles)}")
    print(f"Total words: {sum(article.word_count for article in articles):,}")
    
    categories = {}
    for article in articles:
        categories[article.category] = categories.get(article.category, 0) + 1
    
    print(f"\nArticles by category:")
    for category, count in categories.items():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
