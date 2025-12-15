"""
Example usage of the RAG Support Bot
This script demonstrates how to use the API programmatically
"""
import requests
import json


class RAGClient:
    """Simple client for the RAG Support Bot API"""
    # This client wraps the RAG Support Bot REST API for easy programmatic access
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def ask(self, question: str, top_k: int = 5):
        """Ask a question"""
        response = requests.post(
            f"{self.base_url}/ask",
            json={"question": question, "top_k": top_k}
        )
        response.raise_for_status()
        return response.json()
    
    def health(self):
        """Check health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def stats(self):
        """Get stats"""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage"""
    
    # Create client
    client = RAGClient("http://localhost:8000")
    
    # Check health
    print("Checking API health...")
    health = client.health()
    print(f"Status: {health['status']}")
    print(f"Documents in database: {health['collection_count']}\n")
    
    if health['collection_count'] == 0:
        print("Error: No documents indexed. Please run the indexer first!")
        print("Run: python indexer.py --reset")
        return
    
    # Get stats
    print("Getting statistics...")
    stats = client.stats()
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Embedding model: {stats['embedding_model']}")
    print(f"Chat model: {stats['chat_model']}\n")
    
    # Example questions
    questions = [
        "What is this website about?",
        "How do I get started?",
        "What are the main features?",
    ]
    
    print("Asking questions...\n")
    print("=" * 60)
    
    for question in questions:
        print(f"\nQ: {question}")
        print("-" * 60)
        
        try:
            result = client.ask(question, top_k=3)
            print(f"A: {result['answer']}\n")
            
            if result['sources']:
                print("Sources:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['title']}")
                    print(f"     {source['url']}")
            
            print(f"\n(Used {result['context_used']} context chunks)")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 60)


if __name__ == "__main__":
    main()

