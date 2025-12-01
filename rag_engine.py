"""
RAG Engine: Combines retrieval and generation
"""
from openai import OpenAI
from typing import List, Dict, Optional
import config
from vector_store import VectorStore


class RAGEngine:
    """Retrieval Augmented Generation engine for Q&A"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.vector_store = VectorStore()
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context from vector store
        """
        results = self.vector_store.query(query, n_results=top_k)
        
        # Format results
        contexts = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                context = {
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                }
                contexts.append(context)
        
        return contexts
    
    def generate_answer(self, query: str, contexts: List[Dict]) -> Dict:
        """
        Generate answer using retrieved context and LLM
        """
        # Build context string
        context_text = "\n\n".join([
            f"[Source: {ctx['metadata'].get('title', 'Unknown')}]\n{ctx['text']}"
            for ctx in contexts
        ])
        
        # Create system prompt
        system_prompt = """You are a helpful support assistant. Answer questions based ONLY on the provided context from the website content.

Rules:
1. Only use information from the provided context
2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer that question based on the available content."
3. Be concise and accurate
4. If you quote or reference specific information, mention the source
5. Do not make up or assume information not present in the context"""
        
        # Create user prompt
        user_prompt = f"""Context from website:
{context_text}

Question: {query}

Please provide an answer based only on the context above."""
        
        try:
            # Generate response
            response = self.client.chat.completions.create(
                model=config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Prepare sources
            sources = [
                {
                    'title': ctx['metadata'].get('title', 'Unknown'),
                    'url': ctx['metadata'].get('url', '')
                }
                for ctx in contexts
            ]
            
            # Remove duplicates
            unique_sources = []
            seen_urls = set()
            for source in sources:
                if source['url'] not in seen_urls:
                    unique_sources.append(source)
                    seen_urls.add(source['url'])
            
            return {
                'answer': answer,
                'sources': unique_sources,
                'context_used': len(contexts)
            }
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'context_used': 0
            }
    
    def answer_question(self, query: str, top_k: int = None) -> Dict:
        """
        Main method: Retrieve context and generate answer
        """
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        # Retrieve relevant context
        contexts = self.retrieve_context(query, top_k=top_k)
        
        if not contexts:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'context_used': 0
            }
        
        # Generate answer
        result = self.generate_answer(query, contexts)
        
        return result


if __name__ == "__main__":
    # Test the RAG engine
    engine = RAGEngine()
    
    test_query = "What is this website about?"
    result = engine.answer_question(test_query)
    
    print(f"Question: {test_query}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources used: {len(result['sources'])}")
    for source in result['sources']:
        print(f"  - {source['title']}: {source['url']}")

