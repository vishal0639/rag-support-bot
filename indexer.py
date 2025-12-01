"""
Indexer: Crawls website, processes content, and stores in vector database
"""
import config
from crawler import WebCrawler
from text_processor import TextProcessor
from vector_store import VectorStore
import json
import os
from datetime import datetime


class Indexer:
    """Main indexer class that orchestrates the crawling and indexing process"""
    
    def __init__(self, target_url: str = None, max_pages: int = None):
        self.target_url = target_url or config.TARGET_WEBSITE
        self.max_pages = max_pages or config.MAX_PAGES
        
        # Initialize components
        self.crawler = WebCrawler(self.target_url, self.max_pages)
        self.processor = TextProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStore()
    
    def save_crawled_data(self, pages: list, filename: str = "crawled_data.json"):
        """Save crawled data to a JSON file for backup"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'target_url': self.target_url,
            'total_pages': len(pages),
            'pages': pages
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved crawled data to {filename}")
    
    def load_crawled_data(self, filename: str = "crawled_data.json") -> list:
        """Load previously crawled data from JSON file"""
        if not os.path.exists(filename):
            return None
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {data['total_pages']} pages from {filename}")
        return data['pages']
    
    def run(self, use_cached: bool = False, reset: bool = False):
        """
        Run the complete indexing pipeline
        
        Args:
            use_cached: Use cached crawled data if available
            reset: Reset the vector store before indexing
        """
        print("=" * 60)
        print("RAG Support Bot - Indexing Pipeline")
        print("=" * 60)
        
        # Step 1: Reset vector store if requested
        if reset:
            print("\n[1/4] Resetting vector store...")
            self.vector_store.reset_collection()
        else:
            print("\n[1/4] Skipping reset (use reset=True to reset)")
        
        # Step 2: Crawl or load cached data
        print("\n[2/4] Crawling website...")
        
        if use_cached:
            pages = self.load_crawled_data()
            if pages is None:
                print("No cached data found, starting fresh crawl...")
                pages = self.crawler.crawl()
                self.save_crawled_data(pages)
        else:
            pages = self.crawler.crawl()
            self.save_crawled_data(pages)
        
        if not pages:
            print("ERROR: No pages crawled. Exiting.")
            return
        
        # Step 3: Process and chunk documents
        print("\n[3/4] Processing and chunking documents...")
        chunks = self.processor.process_documents(pages)
        
        if not chunks:
            print("ERROR: No chunks created. Exiting.")
            return
        
        print(f"Created {len(chunks)} chunks from {len(pages)} pages")
        
        # Step 4: Generate embeddings and store in vector database
        print("\n[4/4] Generating embeddings and storing in vector database...")
        self.vector_store.add_documents(chunks)
        
        # Summary
        print("\n" + "=" * 60)
        print("Indexing Complete!")
        print("=" * 60)
        print(f"Target URL: {self.target_url}")
        print(f"Pages crawled: {len(pages)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Vector store count: {self.vector_store.get_collection_count()}")
        print("\nYou can now start the API server with: python main.py")
        print("=" * 60)


def main():
    """Main entry point for the indexer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index website content for RAG bot')
    parser.add_argument(
        '--url',
        type=str,
        help='Target website URL (overrides .env)',
        default=None
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum pages to crawl (overrides .env)',
        default=None
    )
    parser.add_argument(
        '--use-cached',
        action='store_true',
        help='Use cached crawled data if available'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset vector store before indexing'
    )
    
    args = parser.parse_args()
    
    # Create indexer
    indexer = Indexer(
        target_url=args.url,
        max_pages=args.max_pages
    )
    
    # Run indexing
    indexer.run(use_cached=args.use_cached, reset=args.reset)


if __name__ == "__main__":
    main()

