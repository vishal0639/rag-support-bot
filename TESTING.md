# Testing Guide

## Overview

This document provides comprehensive testing instructions for the RAG Support Bot.

## Testing Components

### 1. Individual Component Tests

Each module can be tested independently:

#### Test Crawler
```bash
python crawler.py
```
This will test the crawler with the URL from config.

#### Test Text Processor
```bash
python text_processor.py
```
This will test chunking on sample text.

#### Test Vector Store
```bash
python vector_store.py
```
This will test the vector database connection.

#### Test RAG Engine
```bash
python rag_engine.py
```
This will test the complete RAG pipeline (requires indexed data).

### 2. Full Pipeline Test

#### Step 1: Index Test Website
```bash
# Use a small, fast website for testing
python indexer.py --url https://example.com --max-pages 5 --reset
```

Expected output:
```
====================================================
RAG Support Bot - Indexing Pipeline
====================================================

[1/4] Resetting vector store...
[2/4] Crawling website...
Crawling (1/5): https://example.com
...
[3/4] Processing and chunking documents...
Created X chunks from Y pages
[4/4] Generating embeddings and storing in vector database...
...
Indexing Complete!
```

#### Step 2: Start API Server
```bash
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 3: Run API Tests
In a new terminal:
```bash
python test_api.py
```

Expected output:
```
====================================================
RAG Support Bot API - Test Suite
====================================================

[Test 1] Testing root endpoint...
Status: 200
✓ Root endpoint working

[Test 2] Testing health endpoint...
Status: 200
✓ Health endpoint working

[Test 3] Testing stats endpoint...
Status: 200
✓ Stats endpoint working

[Test 4] Testing ask endpoint...
Status: 200
✓ Ask endpoint working

[Test 5] Testing validation...
Status: 422
✓ Validation working correctly

====================================================
Test suite completed!
====================================================
```

### 3. Manual Testing with cURL

#### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "collection_count": 15
}
```

#### Get Statistics
```bash
curl http://localhost:8000/stats
```

Expected response:
```json
{
  "total_chunks": 15,
  "embedding_model": "text-embedding-ada-002",
  "chat_model": "gpt-3.5-turbo",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

#### Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this website about?"}'
```

Expected response:
```json
{
  "question": "What is this website about?",
  "answer": "This website is about...",
  "sources": [
    {
      "title": "Example Domain",
      "url": "https://example.com"
    }
  ],
  "context_used": 5
}
```

### 4. Postman Testing

#### Import Collection
1. Open Postman
2. Click "Import"
3. Select `POSTMAN_COLLECTION.json`
4. Run requests from the collection

#### Test Scenarios

**Scenario 1: Basic Q&A**
1. Run "Health Check" - should return healthy status
2. Run "Ask Question" - should return an answer
3. Verify sources are included

**Scenario 2: Custom Parameters**
1. Run "Ask Question - Custom top_k"
2. Verify response uses specified number of chunks

**Scenario 3: Error Handling**
1. Modify request to send empty question
2. Should receive 422 validation error

### 5. Integration Testing with Example Client

```bash
python example_usage.py
```

This will:
1. Check API health
2. Get statistics
3. Ask multiple sample questions
4. Display answers and sources

Expected output:
```
Checking API health...
Status: healthy
Documents in database: 15

Getting statistics...
Total chunks: 15
...

Asking questions...
====================================================

Q: What is this website about?
------------------------------------------------------------
A: This website is about example domains...

Sources:
  1. Example Domain
     https://example.com

(Used 3 context chunks)
====================================================
```

## Test Cases

### Positive Test Cases

| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Valid question | "What is Python?" | Answer with sources |
| Empty database check | health endpoint | collection_count > 0 |
| Stats retrieval | stats endpoint | Valid statistics |
| Custom top_k | top_k=3 | Uses 3 chunks |

### Negative Test Cases

| Test Case | Input | Expected Error |
|-----------|-------|----------------|
| Empty question | "" | 422 Validation Error |
| Invalid top_k | top_k=100 | 422 Validation Error |
| Missing question field | {} | 422 Validation Error |
| Server not running | any request | Connection Error |
| Empty vector store | ask before indexing | 400 Bad Request |

## Performance Testing

### Test Indexing Speed
```bash
time python indexer.py --url https://example.com --max-pages 10 --reset
```

Track:
- Total time
- Pages per second
- Chunks generated
- API calls made

### Test Query Speed
```bash
time curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "test question"}'
```

Track:
- Response time
- Consistency across multiple queries

## Validation Checklist

Before submitting:

- [ ] All components test successfully individually
- [ ] Full indexing pipeline completes without errors
- [ ] API server starts successfully
- [ ] All API endpoints return expected responses
- [ ] Health check shows indexed documents
- [ ] Questions return relevant answers
- [ ] Sources are correctly attributed
- [ ] Error handling works (empty questions, etc.)
- [ ] Test suite passes all tests
- [ ] Postman collection works
- [ ] Example usage script runs successfully
- [ ] No linter errors in any Python file
- [ ] README is clear and accurate
- [ ] .env.example is complete

## Common Issues and Solutions

### Issue: "Vector store is empty"
```bash
# Solution: Run indexer
python indexer.py --reset
```

### Issue: "OpenAI API key not found"
```bash
# Solution: Check .env file
cat .env  # Should show OPENAI_API_KEY=sk-...
```

### Issue: Server won't start (port in use)
```bash
# Solution: Change port in config.py or kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Issue: Import errors
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

## Test Data Recommendations

For testing, use these websites:

1. **Small/Fast**: https://example.com (1 page)
2. **Medium**: https://python.org (20-30 pages)
3. **Documentation**: https://docs.python.org (50+ pages)

Start with example.com to verify everything works, then scale up.

## Continuous Testing

During development:
```bash
# Terminal 1: Run server with auto-reload
python main.py

# Terminal 2: Run tests after changes
python test_api.py
```

## Success Criteria

A successful test run should:
1. Index at least 1 page
2. Create at least 1 chunk
3. Return answers to questions
4. Include source attribution
5. Handle errors gracefully
6. Complete in reasonable time (<5 min for small sites)

## Reporting Issues

When reporting issues, include:
1. Command run
2. Full error message
3. Environment (OS, Python version)
4. Configuration (.env values - hide API key!)
5. Steps to reproduce

