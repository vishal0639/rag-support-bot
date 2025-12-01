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
            "ask": "/ask (POST)",
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

