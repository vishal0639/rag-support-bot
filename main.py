"""
Main FastAPI application for the RAG Support Bot
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
import config
from rag_engine import RAGEngine

# Initialize FastAPI app
app = FastAPI(
    title="RAG Support Bot API",
    description="A Q&A support bot using Retrieval Augmented Generation",
    version="1.0.0"
)

# Initialize RAG engine
rag_engine = RAGEngine()


# Request/Response Models
class CrawlRequest(BaseModel):
    """Request model for crawling a website"""
    base_url: str = Field(..., description="Base URL to crawl", min_length=1)
    max_pages: Optional[int] = Field(
        default=50,
        description="Maximum number of pages to crawl",
        ge=1,
        le=200
    )
    reset: Optional[bool] = Field(
        default=False,
        description="Reset vector store before crawling"
    )


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., description="The question to ask", min_length=1)
    top_k: Optional[int] = Field(
        default=None,
        description="Number of context chunks to retrieve (default: 5)",
        ge=1,
        le=10
    )


class Source(BaseModel):
    """Source information model"""
    title: str
    url: str


class QuestionResponse(BaseModel):
    """Response model for answers"""
    question: str
    answer: str
    sources: List[Source]
    context_used: int


class CrawlResponse(BaseModel):
    """Crawl response model"""
    status: str
    message: str
    pages_crawled: int
    chunks_created: int
    total_chunks_indexed: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    collection_count: int


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG Support Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "crawl": "/crawl (POST)",
            "ask": "/ask (POST)",
            "regenerate": "/regenerate (POST)",
            "stats": "/stats",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint
    Returns the status of the service and number of documents in the vector store
    """
    try:
        count = rag_engine.vector_store.get_collection_count()
        return {
            "status": "healthy",
            "collection_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/ask", response_model=QuestionResponse, tags=["Q&A"])
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on crawled website content
    
    The bot will:
    1. Retrieve relevant context from the vector database
    2. Generate an answer using the LLM based only on the retrieved context
    3. Return the answer with sources
    """
    try:
        # Check if vector store has data
        if rag_engine.vector_store.get_collection_count() == 0:
            raise HTTPException(
                status_code=400,
                detail="Vector store is empty. Please run the indexing process first."
            )
        
        # Get answer from RAG engine
        result = rag_engine.answer_question(
            query=request.question,
            top_k=request.top_k
        )
        
        # Format response
        response = {
            "question": request.question,
            "answer": result['answer'],
            "sources": result['sources'],
            "context_used": result['context_used']
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/crawl", response_model=CrawlResponse, tags=["Indexing"])
async def crawl_website(request: CrawlRequest):
    """
    Crawl a website and index its content into the vector database
    
    This endpoint will:
    1. Crawl the specified website (respecting same-domain policy)
    2. Extract and clean text content from each page
    3. Chunk the content into manageable pieces
    4. Generate embeddings for each chunk
    5. Store everything in the vector database
    
    Note: This operation may take several minutes depending on the number of pages.
    For production use, consider implementing as a background task.
    """
    try:
        from indexer import Indexer
        
        print(f"Starting crawl request for: {request.base_url}")
        
        # Create indexer with specified parameters
        indexer = Indexer(
            target_url=request.base_url,
            max_pages=request.max_pages
        )
        
        # Reset if requested
        if request.reset:
            indexer.vector_store.reset_collection()
        
        # Crawl the website
        pages = indexer.crawler.crawl()
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No pages were successfully crawled. Please check the URL."
            )
        
        # Save crawled data
        indexer.save_crawled_data(pages)
        
        # Process and chunk documents
        chunks = indexer.processor.process_documents(pages)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks were created from the crawled content."
            )
        
        # Generate embeddings and store
        indexer.vector_store.add_documents(chunks)
        
        # Get final count
        total_count = indexer.vector_store.get_collection_count()
        
        return {
            "status": "success",
            "message": f"Successfully crawled and indexed {request.base_url}",
            "pages_crawled": len(pages),
            "chunks_created": len(chunks),
            "total_chunks_indexed": total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")


@app.post("/regenerate", tags=["Indexing"])
async def regenerate_embeddings():
    """
    Regenerate embeddings from cached crawled data
    
    This is useful when:
    - You want to change the embedding model
    - You want to adjust chunking parameters
    - You want to re-index without re-crawling
    
    Note: This requires that you have previously run the /crawl endpoint or indexer.py
    which saves crawled data to crawled_data.json
    """
    try:
        from indexer import Indexer
        import os
        
        # Create indexer
        indexer = Indexer()
        
        # Load cached crawl data
        if not os.path.exists("crawled_data.json"):
            raise HTTPException(
                status_code=400,
                detail="No cached crawl data found. Please run /crawl endpoint first."
            )
        
        pages = indexer.load_crawled_data()
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="Failed to load cached data."
            )
        
        # Reset vector store
        indexer.vector_store.reset_collection()
        
        # Re-process and re-index
        chunks = indexer.processor.process_documents(pages)
        indexer.vector_store.add_documents(chunks)
        
        # Get final count
        total_count = indexer.vector_store.get_collection_count()
        
        return {
            "status": "success",
            "message": "Embeddings regenerated successfully from cached data",
            "pages_processed": len(pages),
            "chunks_created": len(chunks),
            "total_chunks_indexed": total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")


@app.get("/stats", tags=["General"])
async def get_stats():
    """Get statistics about the indexed content"""
    try:
        count = rag_engine.vector_store.get_collection_count()
        return {
            "total_chunks": count,
            "embedding_model": config.EMBEDDING_MODEL,
            "chat_model": config.CHAT_MODEL,
            "chunk_size": config.CHUNK_SIZE,
            "chunk_overlap": config.CHUNK_OVERLAP
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

