"""
Text processing: cleaning and chunking text content
"""
import re
import tiktoken
from typing import List, Dict
import config


class TextProcessor:
    """Handles text cleaning and chunking"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model(config.EMBEDDING_MODEL)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict[str, any]]:
        """
        Split text into chunks based on token count
        Returns list of chunks with metadata
        """
        # Clean the text first
        text = self.clean_text(text)
        
        # Tokenize the text
        tokens = self.encoding.encode(text)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            # Get chunk
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk with metadata
            chunk = {
                'text': chunk_text,
                'token_count': len(chunk_tokens),
                'chunk_index': len(chunks)
            }
            
            # Add metadata if provided
            if metadata:
                chunk.update(metadata)
            
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Avoid infinite loop on small texts
            if end >= len(tokens):
                break
        
        return chunks
    
    def process_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """
        Process multiple documents into chunks
        Each document should have 'content', 'url', and 'title'
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            url = doc.get('url', '')
            title = doc.get('title', '')
            
            if not content.strip():
                continue
            
            # Create metadata
            metadata = {
                'url': url,
                'title': title
            }
            
            # Chunk the document
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        print(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        
        return all_chunks


if __name__ == "__main__":
    # Test the processor
    processor = TextProcessor()
    
    test_doc = {
        'content': 'This is a test document. ' * 100,
        'url': 'https://example.com/test',
        'title': 'Test Document'
    }
    
    chunks = processor.process_documents([test_doc])
    print(f"Created {len(chunks)} chunks")
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Token count: {chunks[0]['token_count']}")

