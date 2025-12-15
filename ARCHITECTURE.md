# System Architecture - RAG Support Bot

**Version:** 2.0.0  
**Last Updated:** December 15, 2025

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG SUPPORT BOT                         │
│                         Version 2.0.0                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼────────┐            ┌────────▼─────────┐
        │  CLI Interface │            │   REST API       │
        │   (Terminal)   │            │   (FastAPI)      │
        └───────┬────────┘            └────────┬─────────┘
                │                               │
        ┌───────▼────────┐            ┌────────▼─────────┐
        │  indexer.py    │            │   main.py        │
        │  generate_faq  │            │  (Uvicorn)       │
        └───────┬────────┘            └────────┬─────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                ┌───────────────▼────────────────┐
                │      CORE ENGINE               │
                │                                │
                │  ┌──────────────────────────┐ │
                │  │    RAG Engine            │ │
                │  │  (rag_engine.py)         │ │
                │  │                          │ │
                │  │  • Retrieve Context     │ │
                │  │  • Generate Answer      │ │
                │  │  • Source Attribution   │ │
                │  └────────┬─────────────────┘ │
                └───────────┼──────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼──────┐
│   Crawler    │   │ Text Processor  │   │   Vector   │
│              │   │                 │   │   Store    │
│ • HTTP Get   │──▶│ • Clean Text   │──▶│            │
│ • Parse HTML │   │ • Chunk Text    │   │ • Embed    │
│ • Extract    │   │ • Tokenize      │   │ • Store    │
│ • Rate Limit │   │ • Metadata      │   │ • Search   │
└──────────────┘   └─────────────────┘   └─────┬──────┘
                                                │
                                        ┌───────▼────────┐
                                        │   ChromaDB     │
                                        │  (Persistent)  │
                                        └───────┬────────┘
                                                │
                                        ┌───────▼────────┐
                                        │  OpenAI API    │
                                        │                │
                                        │ • Embeddings   │
                                        │ • GPT-3.5      │
                                        └────────────────┘
```

---

## Component Architecture

### 1. API Layer (main.py)

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
├─────────────────────────────────────────────────┤
│                                                 │
│  GET /              → API Info                  │
│  GET /health        → Health Check              │
│  GET /stats         → Statistics                │
│  POST /ask          → Question Answering        │
│  POST /crawl        → Crawl & Index Website ✨  │
│  POST /regenerate   → Regenerate Embeddings ✨  │
│                                                 │
├─────────────────────────────────────────────────┤
│         Pydantic Models (Validation)            │
│  • CrawlRequest     • CrawlResponse             │
│  • QuestionRequest  • QuestionResponse          │
│  • HealthResponse   • Source                    │
└─────────────────────────────────────────────────┘
```

### 2. RAG Engine (rag_engine.py)

```
┌─────────────────────────────────────────────────┐
│                 RAG Engine                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  retrieve_context(query, top_k)                 │
│    ├─ Generate query embedding                  │
│    ├─ Search vector store                       │
│    └─ Return top K chunks + metadata            │
│                                                 │
│  generate_answer(query, contexts)               │
│    ├─ Build context string                      │
│    ├─ Create system prompt                      │
│    ├─ Call OpenAI GPT-3.5-turbo                 │
│    └─ Extract and deduplicate sources           │
│                                                 │
│  answer_question(query, top_k)                  │
│    ├─ Retrieve context                          │
│    └─ Generate answer                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 3. Crawler (crawler.py)

```
┌─────────────────────────────────────────────────┐
│              Web Crawler                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  crawl(base_url, max_pages)                     │
│    ├─ Validate URL (same domain)                │
│    ├─ Fetch HTML (requests)                     │
│    ├─ Parse HTML (BeautifulSoup + lxml)         │
│    ├─ Extract links                             │
│    ├─ Clean text                                │
│    │   ├─ Remove <script>, <style>              │
│    │   ├─ Remove <nav>, <footer>, <header>      │
│    │   ├─ Extract visible text                  │
│    │   └─ Normalize whitespace                  │
│    ├─ Store page data                           │
│    └─ Rate limit (delay between requests)       │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 4. Text Processor (text_processor.py)

```
┌─────────────────────────────────────────────────┐
│            Text Processor                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  process_documents(pages)                       │
│    ├─ For each page:                            │
│    │   ├─ clean_text()                          │
│    │   │   ├─ Remove extra whitespace           │
│    │   │   ├─ Remove special characters         │
│    │   │   └─ Normalize text                    │
│    │   │                                        │
│    │   └─ chunk_text()                          │
│    │       ├─ Tokenize with tiktoken            │
│    │       ├─ Split into chunks (500 tokens)    │
│    │       ├─ Apply overlap (50 tokens)         │
│    │       └─ Add metadata                      │
│    │           ├─ URL                           │
│    │           ├─ Title                         │
│    │           ├─ Chunk index                   │
│    │           └─ Token count                   │
│    │                                            │
│    └─ Return all chunks                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 5. Vector Store (vector_store.py)

```
┌─────────────────────────────────────────────────┐
│              Vector Store                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  add_documents(chunks, batch_size=100)          │
│    ├─ For each batch:                           │
│    │   ├─ generate_embedding(text)              │
│    │   │   └─ OpenAI text-embedding-ada-002     │
│    │   │       → 1536-dimensional vector        │
│    │   │                                        │
│    │   └─ collection.add()                      │
│    │       ├─ Embeddings                        │
│    │       ├─ Documents (text)                  │
│    │       ├─ Metadata                          │
│    │       └─ IDs                               │
│    │                                            │
│    └─ Persist to disk (./chroma_db)             │
│                                                 │
│  query(query_text, n_results)                   │
│    ├─ Generate query embedding                  │
│    ├─ Similarity search (cosine)                │
│    └─ Return top N results + metadata           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 6. Indexer (indexer.py)

```
┌─────────────────────────────────────────────────┐
│              Indexer Pipeline                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  run(use_cached, reset)                         │
│                                                 │
│    [1] Reset vector store (if reset=True)       │
│         └─ Delete and recreate collection       │
│                                                 │
│    [2] Crawl website (or load cached)           │
│         ├─ WebCrawler.crawl()                   │
│         └─ Save to crawled_data.json            │
│                                                 │
│    [3] Process documents                        │
│         ├─ TextProcessor.process_documents()    │
│         └─ Generate chunks                      │
│                                                 │
│    [4] Generate embeddings & store              │
│         ├─ VectorStore.add_documents()          │
│         └─ Batch processing (100 at a time)     │
│                                                 │
│    [5] Report statistics                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7. FAQ Generator (generate_faq.py) ✨ NEW

```
┌─────────────────────────────────────────────────┐
│            FAQ Generator                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  generate_faq(questions, output_file, title)    │
│                                                 │
│    ├─ Load questions                            │
│    │   ├─ From text file (line by line)         │
│    │   └─ From JSON file (array)                │
│    │                                            │
│    ├─ For each question:                        │
│    │   ├─ RAGEngine.answer_question()           │
│    │   ├─ Format answer                         │
│    │   └─ Add sources                           │
│    │                                            │
│    └─ Save as Markdown                          │
│        ├─ Title                                 │
│        ├─ Questions & answers                   │
│        ├─ Source links                          │
│        └─ Footer                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Indexing Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     │ python indexer.py --url https://example.com --reset
     │
     ▼
┌─────────────────┐
│  Indexer.run()  │
└────┬────────────┘
     │
     ├─ [1] Reset Vector Store
     │      │
     │      ▼
     │  ┌─────────────────┐
     │  │  VectorStore    │
     │  │  .reset()       │
     │  └─────────────────┘
     │
     ├─ [2] Crawl Website
     │      │
     │      ▼
     │  ┌─────────────────────────┐
     │  │  WebCrawler.crawl()     │
     │  │                         │
     │  │  https://example.com    │
     │  │         ↓               │
     │  │  Fetch HTML             │
     │  │         ↓               │
     │  │  Parse with BS4         │
     │  │         ↓               │
     │  │  Extract text           │
     │  │         ↓               │
     │  │  Clean content          │
     │  │         ↓               │
     │  │  Find links             │
     │  │         ↓               │
     │  │  Repeat (up to max)     │
     │  │         ↓               │
     │  │  Return pages[]         │
     │  └────────┬────────────────┘
     │           │
     │           ▼
     │  ┌─────────────────────────┐
     │  │ Save crawled_data.json  │
     │  └─────────────────────────┘
     │
     ├─ [3] Process & Chunk
     │      │
     │      ▼
     │  ┌──────────────────────────────┐
     │  │ TextProcessor                │
     │  │ .process_documents()         │
     │  │                              │
     │  │  For each page:              │
     │  │    Clean text                │
     │  │         ↓                    │
     │  │    Tokenize                  │
     │  │         ↓                    │
     │  │    Split into chunks         │
     │  │         ↓                    │
     │  │    Add metadata              │
     │  │         ↓                    │
     │  │  Return chunks[]             │
     │  └────────┬─────────────────────┘
     │           │
     │           ▼
     ├─ [4] Generate Embeddings & Store
     │      │
     │      ▼
     │  ┌──────────────────────────────┐
     │  │ VectorStore                  │
     │  │ .add_documents()             │
     │  │                              │
     │  │  Batch 1 (100 chunks)        │
     │  │         ↓                    │
     │  │  OpenAI API                  │
     │  │         ↓                    │
     │  │  Get embeddings              │
     │  │         ↓                    │
     │  │  Store in ChromaDB           │
     │  │         ↓                    │
     │  │  Batch 2...                  │
     │  │         ↓                    │
     │  │  Persist to disk             │
     │  └──────────────────────────────┘
     │
     └─ [5] Report Complete
            ↓
     ┌─────────────────┐
     │  ✓ Indexing     │
     │    Complete     │
     └─────────────────┘
```

### Query Flow (POST /ask)

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     │ POST /ask {"question": "What is Python?"}
     │
     ▼
┌─────────────────────────┐
│  FastAPI Endpoint       │
│  /ask                   │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│  RAGEngine              │
│  .answer_question()     │
└────┬────────────────────┘
     │
     ├─ [1] Retrieve Context
     │      │
     │      ▼
     │  ┌──────────────────────────┐
     │  │ VectorStore.query()      │
     │  │                          │
     │  │ "What is Python?"        │
     │  │        ↓                 │
     │  │ Generate embedding       │
     │  │        ↓                 │
     │  │ OpenAI API               │
     │  │        ↓                 │
     │  │ Search ChromaDB          │
     │  │        ↓                 │
     │  │ Cosine similarity        │
     │  │        ↓                 │
     │  │ Top 5 chunks             │
     │  └────────┬─────────────────┘
     │           │
     │           ▼
     ├─ [2] Generate Answer
     │      │
     │      ▼
     │  ┌──────────────────────────┐
     │  │ RAGEngine                │
     │  │ .generate_answer()       │
     │  │                          │
     │  │ Build context string     │
     │  │        ↓                 │
     │  │ Create system prompt:    │
     │  │ "Answer only from        │
     │  │  provided context..."    │
     │  │        ↓                 │
     │  │ Create user prompt:      │
     │  │ "Context: ...            │
     │  │  Question: ...?"         │
     │  │        ↓                 │
     │  │ Call OpenAI GPT-3.5      │
     │  │        ↓                 │
     │  │ Get answer               │
     │  │        ↓                 │
     │  │ Extract sources          │
     │  │        ↓                 │
     │  │ Deduplicate sources      │
     │  └────────┬─────────────────┘
     │           │
     │           ▼
     └─ [3] Format Response
            │
            ▼
     ┌─────────────────────────┐
     │ Return JSON:            │
     │ {                       │
     │   "answer": "...",      │
     │   "sources": [...],     │
     │   "context_used": 5     │
     │ }                       │
     └─────────────────────────┘
```

### Crawl Flow (POST /crawl) ✨ NEW

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     │ POST /crawl {"base_url": "https://example.com"}
     │
     ▼
┌─────────────────────────┐
│  FastAPI Endpoint       │
│  /crawl                 │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│  Create Indexer         │
└────┬────────────────────┘
     │
     ├─ Reset if requested
     ├─ Run crawler
     ├─ Save data
     ├─ Process chunks
     ├─ Generate embeddings
     └─ Store in vector DB
            │
            ▼
     ┌─────────────────────────┐
     │ Return:                 │
     │ {                       │
     │   "status": "success",  │
     │   "pages_crawled": 45,  │
     │   "chunks_created": 234 │
     │ }                       │
     └─────────────────────────┘
```

---

## Technology Stack

### Backend Framework
```
FastAPI (0.104.1+)
├─ Pydantic for data validation
├─ Uvicorn as ASGI server
├─ Async support
└─ Auto-generated API docs
```

### Web Scraping
```
Requests (2.31.0+)
├─ HTTP requests
└─ Session management

BeautifulSoup4 (4.12.2+)
├─ HTML parsing
├─ Text extraction
└─ Link discovery

lxml (4.9.3+)
└─ Fast HTML parser
```

### NLP & Embeddings
```
OpenAI API (1.3.5+)
├─ text-embedding-ada-002
│   ├─ 1536 dimensions
│   └─ $0.0001 per 1K tokens
│
└─ gpt-3.5-turbo
    ├─ Answer generation
    └─ ~$0.002 per 1K tokens

tiktoken (0.5.1+)
└─ Token counting for chunking
```

### Vector Database
```
ChromaDB (0.4.18+)
├─ Persistent storage
├─ Similarity search
├─ Metadata filtering
└─ Local deployment
```

### Configuration
```
python-dotenv (1.0.0+)
└─ Environment variables

config.py
├─ Centralized settings
└─ Easy customization
```

---

## Configuration Architecture

```
Environment Variables (.env)
    ↓
┌─────────────────────────────────┐
│       config.py                 │
├─────────────────────────────────┤
│                                 │
│ OPENAI_API_KEY                  │
│ TARGET_WEBSITE                  │
│ MAX_PAGES                       │
│ CHUNK_SIZE                      │
│ CHUNK_OVERLAP                   │
│ TOP_K_RESULTS                   │
│ API_HOST                        │
│ API_PORT                        │
│ ...                             │
│                                 │
└────────┬────────────────────────┘
         │
         ├─→ crawler.py
         ├─→ text_processor.py
         ├─→ vector_store.py
         ├─→ rag_engine.py
         └─→ main.py
```

---

## Storage Architecture

```
Project Root
│
├─ chroma_db/               (Vector Database)
│  ├─ chroma.sqlite3        (Metadata)
│  └─ vectors/              (Embeddings)
│
├─ crawled_data.json        (Cached crawl data)
│  └─ {
│       "timestamp": "...",
│       "pages": [...]
│     }
│
└─ .env                     (Environment config)
   └─ OPENAI_API_KEY=...
```

---

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                 │
├─────────────────────────────────────────┤
│                                         │
│  [1] Environment Variables              │
│      ├─ API keys in .env                │
│      ├─ Not in version control          │
│      └─ Loaded at runtime               │
│                                         │
│  [2] Input Validation                   │
│      ├─ Pydantic models                 │
│      ├─ Type checking                   │
│      └─ Field validation                │
│                                         │
│  [3] Error Handling                     │
│      ├─ Try-except blocks               │
│      ├─ HTTP exceptions                 │
│      └─ Graceful degradation            │
│                                         │
│  [4] Rate Limiting (Crawling)           │
│      ├─ REQUEST_DELAY                   │
│      └─ Polite crawling                 │
│                                         │
│  [TODO] API Authentication              │
│  [TODO] Rate Limiting (API)             │
│  [TODO] HTTPS/TLS                       │
│                                         │
└─────────────────────────────────────────┘
```

---

## Scalability Considerations

### Current Architecture (Single Instance)
```
Single Process
    ↓
FastAPI + Uvicorn
    ↓
ChromaDB (Local)
    ↓
Local File System
```

### Future Scalability (Multi-Instance)
```
Load Balancer
    ↓
┌───────┬───────┬───────┐
│ API 1 │ API 2 │ API 3 │
└───┬───┴───┬───┴───┬───┘
    │       │       │
    └───────┼───────┘
            ↓
    Shared Vector DB
    (ChromaDB Server)
            ↓
    Shared Storage
    (S3 / Cloud Storage)
```

---

## Monitoring & Observability

### Current
```
Print Statements
    └─ Progress indicators
    └─ Error messages
```

### Recommended
```
Structured Logging
    ├─ Log levels (DEBUG, INFO, WARN, ERROR)
    ├─ JSON format
    └─ Log aggregation

Metrics
    ├─ Request count
    ├─ Response time
    ├─ Error rate
    └─ Cache hit rate

Monitoring
    ├─ Prometheus (metrics)
    ├─ Grafana (dashboards)
    └─ Sentry (error tracking)
```

---

## Deployment Architecture

### Development
```
Local Machine
    ├─ Python virtual environment
    ├─ SQLite (ChromaDB)
    └─ Local file system
```

### Production (Recommended)
```
Cloud Platform (AWS/GCP/Azure)
    ├─ Container (Docker)
    ├─ Orchestration (Kubernetes)
    ├─ Vector DB (Hosted ChromaDB or Pinecone)
    ├─ File Storage (S3/GCS/Blob)
    ├─ Load Balancer
    ├─ Auto-scaling
    └─ Monitoring
```

---

## Performance Characteristics

### Throughput
- **Crawling:** 2-5 pages/second
- **Indexing:** ~100 chunks/batch
- **Query:** <3 seconds typical

### Latency
- **API Response:** 1-5 seconds
- **Embedding Generation:** 100ms per chunk
- **Vector Search:** <100ms

### Resource Usage
- **Memory:** 200-500 MB
- **Disk:** 10-50 MB per 50 pages
- **Network:** Minimal (rate-limited)

---

## Error Handling Architecture

```
┌─────────────────────────────────────┐
│         Error Handling              │
├─────────────────────────────────────┤
│                                     │
│  Application Layer                  │
│    ├─ Try-except in all functions   │
│    ├─ Specific error messages       │
│    └─ Graceful degradation          │
│                                     │
│  API Layer                          │
│    ├─ HTTPException for API errors  │
│    ├─ Status codes (400, 500, etc.) │
│    └─ JSON error responses          │
│                                     │
│  External Services                  │
│    ├─ OpenAI API errors             │
│    ├─ Network errors                │
│    └─ Rate limiting                 │
│                                     │
└─────────────────────────────────────┘
```

---

## Summary

This architecture provides:

✅ **Modularity** - Clear separation of concerns  
✅ **Scalability** - Can scale horizontally  
✅ **Maintainability** - Easy to understand and modify  
✅ **Extensibility** - Simple to add new features  
✅ **Reliability** - Comprehensive error handling  
✅ **Performance** - Optimized with batch processing  
✅ **Security** - Environment-based configuration  
✅ **Documentation** - Well-documented codebase  

---

*Architecture version: 2.0.0*  
*Last updated: December 15, 2025*

