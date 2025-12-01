"""
Vector database for storing and retrieving embeddings
"""
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from typing import List, Dict, Optional
import config


class VectorStore:
    """Manages vector embeddings storage and retrieval using ChromaDB"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=config.COLLECTION_NAME
            )
            print(f"Loaded existing collection: {config.COLLECTION_NAME}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=config.COLLECTION_NAME,
                metadata={"description": "Website content embeddings"}
            )
            print(f"Created new collection: {config.COLLECTION_NAME}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=config.EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, any]], batch_size: int = 100):
        """
        Add document chunks to the vector store
        Processes in batches for efficiency
        """
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Prepare batch data
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            for idx, chunk in enumerate(batch):
                chunk_id = f"chunk_{i + idx}"
                text = chunk['text']
                
                # Generate embedding
                embedding = self.generate_embedding(text)
                
                # Prepare metadata
                metadata = {
                    'url': chunk.get('url', ''),
                    'title': chunk.get('title', ''),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'token_count': chunk.get('token_count', 0)
                }
                
                documents.append(text)
                embeddings.append(embedding)
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1}")
        
        print("All chunks added successfully!")
    
    def query(self, query_text: str, n_results: int = 5) -> Dict:
        """
        Query the vector store with a question
        Returns top k most similar chunks
        """
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query_text)
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the collection"""
        self.chroma_client.delete_collection(name=config.COLLECTION_NAME)
        print(f"Deleted collection: {config.COLLECTION_NAME}")
    
    def reset_collection(self):
        """Reset the collection by deleting and recreating it"""
        try:
            self.delete_collection()
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "Website content embeddings"}
        )
        print(f"Reset collection: {config.COLLECTION_NAME}")


if __name__ == "__main__":
    # Test the vector store
    store = VectorStore()
    
    test_chunks = [
        {
            'text': 'This is a test document about Python programming.',
            'url': 'https://example.com/python',
            'title': 'Python Guide',
            'chunk_index': 0,
            'token_count': 10
        }
    ]
    
    # Add documents
    # store.add_documents(test_chunks)
    
    # Query
    # results = store.query("What is Python?", n_results=1)
    # print(f"Query results: {results}")
    
    print(f"Collection count: {store.get_collection_count()}")

