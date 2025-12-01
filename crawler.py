"""
Web crawler to scrape website content
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Set, Dict
import config


class WebCrawler:
    """Crawls a website and extracts text content from pages"""
    
    def __init__(self, base_url: str, max_pages: int = 50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_content: List[Dict[str, str]] = []
        self.domain = urlparse(base_url).netloc
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain
    
    def clean_text(self, soup: BeautifulSoup) -> str:
        """Extract and clean text from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def get_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(current_url, link['href'])
            # Remove fragments
            url = url.split('#')[0]
            if self.is_valid_url(url) and url not in self.visited_urls:
                links.append(url)
        return links
    
    def crawl_page(self, url: str) -> bool:
        """Crawl a single page and extract content"""
        try:
            print(f"Crawling: {url}")
            response = requests.get(
                url,
                timeout=config.REQUEST_TIMEOUT,
                headers={'User-Agent': 'Mozilla/5.0 (RAG Support Bot)'}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract text content
            text = self.clean_text(soup)
            
            if text.strip():
                self.pages_content.append({
                    'url': url,
                    'content': text,
                    'title': soup.title.string if soup.title else url
                })
            
            # Get links for further crawling
            links = self.get_links(soup, url)
            
            # Add new links to queue
            for link in links:
                if len(self.visited_urls) < self.max_pages:
                    if link not in self.visited_urls:
                        self.crawl_page(link)
            
            return True
            
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return False
    
    def crawl(self) -> List[Dict[str, str]]:
        """Start crawling from the base URL"""
        print(f"Starting crawl of {self.base_url}")
        print(f"Max pages: {self.max_pages}")
        
        urls_to_visit = [self.base_url]
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            try:
                print(f"Crawling ({len(self.visited_urls)}/{self.max_pages}): {url}")
                response = requests.get(
                    url,
                    timeout=config.REQUEST_TIMEOUT,
                    headers={'User-Agent': 'Mozilla/5.0 (RAG Support Bot)'}
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Extract text content
                text = self.clean_text(soup)
                
                if text.strip():
                    self.pages_content.append({
                        'url': url,
                        'content': text,
                        'title': soup.title.string if soup.title else url
                    })
                
                # Get links for further crawling
                links = self.get_links(soup, url)
                urls_to_visit.extend(links)
                
                # Be polite - add delay between requests
                time.sleep(config.REQUEST_DELAY)
                
            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")
                continue
        
        print(f"\nCrawling completed!")
        print(f"Total pages crawled: {len(self.pages_content)}")
        
        return self.pages_content


if __name__ == "__main__":
    # Test the crawler
    crawler = WebCrawler(config.TARGET_WEBSITE, config.MAX_PAGES)
    pages = crawler.crawl()
    print(f"\nCrawled {len(pages)} pages")
    if pages:
        print(f"Sample page: {pages[0]['title']}")
        print(f"Content preview: {pages[0]['content'][:200]}...")

