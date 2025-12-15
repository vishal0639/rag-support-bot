# RAG Support Bot

A Q&A support bot built with Retrieval Augmented Generation (RAG) that answers questions based on crawled website content.

## Overview

This project implements a complete RAG pipeline that:
1. Crawls a target website and extracts content
2. Cleans and chunks the text into manageable pieces
3. Generates embeddings using OpenAI's API
4. Stores embeddings in a ChromaDB vector database
5. Provides a FastAPI endpoint to answer questions using only the crawled content

## Features

- **Web Crawler**: Automatically crawls website pages and extracts clean text content
- **Text Processing**: Intelligent chunking with token-aware splitting and overlap
- **Vector Search**: Fast semantic search using ChromaDB
- **RAG Engine**: Combines retrieval and generation for accurate answers
- **REST API**: Clean FastAPI interface for asking questions
- **Source Attribution**: Answers include source references from the crawled content

## Project Structure

```
rag-support-bot/
├── config.py              # Configuration settings
├── crawler.py             # Web crawler implementation
├── text_processor.py      # Text cleaning and chunking
├── vector_store.py        # Vector database operations
├── rag_engine.py          # RAG logic (retrieval + generation)
├── indexer.py             # Pipeline orchestration
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for crawling

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd rag-support-bot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
TARGET_WEBSITE=https://example.com
MAX_PAGES=50
```

**Important**: Get your OpenAI API key from https://platform.openai.com/api-keys

## Usage

### Quick Start (Two Options)

#### Option A: Using the API (Recommended)

1. **Start the API Server**:
```bash
python main.py
```

2. **Crawl and Index via API**:
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "https://docs.python.org", "max_pages": 20, "reset": true}'
```

3. **Ask Questions**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

#### Option B: Using Command Line

1. **Index the Website**:
```bash
python indexer.py --url https://docs.python.org --max-pages 20 --reset
```

**Options**:
- `--url <URL>`: Specify target URL (overrides .env)
- `--max-pages <N>`: Maximum pages to crawl (overrides .env)
- `--reset`: Reset vector database before indexing
- `--use-cached`: Use previously crawled data if available

2. **Start the API Server**

Once indexing is complete, start the FastAPI server:

```bash
python main.py
```

The server will start at `http://localhost:8000`

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Step 3: Ask Questions

You can now ask questions about the crawled content!

#### Using curl

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is Python?\"}"
```

#### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "What is Python?", "top_k": 5}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

#### Using Postman

1. Create a new POST request
2. URL: `http://localhost:8000/ask`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "question": "What is Python?",
  "top_k": 5
}
```

#### Response Format

```json
{
  "question": "What is Python?",
  "answer": "Python is a high-level programming language...",
  "sources": [
    {
      "title": "Python Documentation",
      "url": "https://docs.python.org/intro"
    }
  ],
  "context_used": 5
}
```

## API Endpoints

### `GET /`
Root endpoint with API information

### `GET /health`
Health check endpoint
- Returns service status
- Shows number of indexed chunks

### `POST /crawl` ✨ NEW
Crawl and index a website via API

**Request Body**:
```json
{
  "base_url": "https://example.com",
  "max_pages": 50,  // Optional: default 50
  "reset": false    // Optional: reset vector store before crawling
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Successfully crawled and indexed https://example.com",
  "pages_crawled": 45,
  "chunks_created": 234,
  "total_chunks_indexed": 234
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "https://docs.python.org", "max_pages": 20, "reset": true}'
```

### `POST /ask`
Ask a question and get an answer

**Request Body**:
```json
{
  "question": "Your question here",
  "top_k": 5  // Optional: number of context chunks (1-10)
}
```

**Response**:
```json
{
  "question": "string",
  "answer": "string",
  "sources": [{"title": "string", "url": "string"}],
  "context_used": 0
}
```

### `POST /regenerate` ✨ NEW
Regenerate embeddings from cached crawled data

This is useful when you want to:
- Change the embedding model
- Adjust chunking parameters
- Re-index without re-crawling

**Request Body**: None (uses cached `crawled_data.json`)

**Response**:
```json
{
  "status": "success",
  "message": "Embeddings regenerated successfully from cached data",
  "pages_processed": 45,
  "chunks_created": 234,
  "total_chunks_indexed": 234
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/regenerate"
```

### `GET /stats`
Get statistics about indexed content

## Configuration

Edit `config.py` or use environment variables:

### Crawling Settings
- `TARGET_WEBSITE`: Base URL to crawl
- `MAX_PAGES`: Maximum number of pages to crawl
- `REQUEST_TIMEOUT`: Request timeout in seconds
- `REQUEST_DELAY`: Delay between requests (be polite!)

### Chunking Settings
- `CHUNK_SIZE`: Tokens per chunk (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)

### Model Settings
- `EMBEDDING_MODEL`: OpenAI embedding model (default: text-embedding-ada-002)
- `CHAT_MODEL`: OpenAI chat model (default: gpt-3.5-turbo)

### Retrieval Settings
- `TOP_K_RESULTS`: Number of chunks to retrieve (default: 5)

## How It Works

### 1. Crawling
The crawler starts from a base URL and recursively visits pages within the same domain:
- Extracts clean text from HTML
- Removes navigation, scripts, and styling
- Respects rate limits with delays between requests
- Saves data locally for caching

### 2. Text Processing
- Cleans and normalizes text
- Splits into chunks based on token count (not characters)
- Maintains overlap between chunks for context continuity
- Preserves metadata (URL, title, chunk index)

### 3. Embedding Generation
- Uses OpenAI's `text-embedding-ada-002` model
- Generates 1536-dimensional vectors
- Processes in batches for efficiency

### 4. Vector Storage
- Stores embeddings in ChromaDB
- Persists to disk for reuse
- Enables fast similarity search

### 5. Question Answering
- Converts question to embedding
- Retrieves top K most similar chunks
- Feeds context to LLM with strict instructions
- LLM generates answer based ONLY on provided context

## Example Workflow

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 2. Install dependencies
pip install -r requirements.txt

# 3. Index a website
python indexer.py --url https://docs.python.org --max-pages 30 --reset

# 4. Start the server
python main.py

# 5. Ask questions (in another terminal)
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"How do I install Python?\"}"
```

## Testing

### Manual Testing

1. **Test the crawler**:
```bash
python crawler.py
```

2. **Test the text processor**:
```bash
python text_processor.py
```

3. **Test the vector store**:
```bash
python vector_store.py
```

4. **Test the RAG engine**:
```bash
python rag_engine.py
```

### Testing with Postman

Import these requests into Postman:

**1. Health Check**
- Method: GET
- URL: `http://localhost:8000/health`

**2. Ask Question**
- Method: POST
- URL: `http://localhost:8000/ask`
- Body: `{"question": "What is this website about?"}`

**3. Get Stats**
- Method: GET
- URL: `http://localhost:8000/stats`

## Troubleshooting

### Issue: "Vector store is empty"
**Solution**: Run the indexer first: `python indexer.py --reset`

### Issue: "OpenAI API key not found"
**Solution**: Check your `.env` file has `OPENAI_API_KEY=sk-...`

### Issue: Crawler gets blocked
**Solution**: Increase `REQUEST_DELAY` in `config.py` or reduce `MAX_PAGES`

### Issue: Out of memory during indexing
**Solution**: Reduce `MAX_PAGES` or `CHUNK_SIZE` in configuration

### Issue: Poor answer quality
**Solution**: 
- Increase `TOP_K_RESULTS` to retrieve more context
- Adjust `CHUNK_SIZE` for better chunking
- Check if the crawled content is relevant

## Best Practices

1. **Start Small**: Test with `MAX_PAGES=10` before crawling large sites
2. **Be Polite**: Keep `REQUEST_DELAY` at least 0.5 seconds
3. **Cache Data**: Use `--use-cached` flag to avoid re-crawling
4. **Monitor Costs**: OpenAI API charges for embeddings and chat completions
5. **Test Questions**: Try specific questions about your crawled content

## Limitations

- Only crawls pages from the same domain
- Requires OpenAI API key (costs apply)
- Answer quality depends on crawled content quality
- Does not handle dynamic JavaScript content
- Limited to text content (no images/videos)

## Cost Estimation

For a typical website with 50 pages:
- **Indexing** (one-time): ~$0.10 - $0.50
  - Embeddings: ~$0.0001 per 1K tokens
- **Each Question**: ~$0.001 - $0.01
  - Retrieval: free (ChromaDB)
  - Answer generation: ~$0.002 per request

## FAQ Generator

Generate a Markdown FAQ document from a list of questions:

### Basic Usage
```bash
# Use default example questions
python generate_faq.py

# Use custom questions from a file
python generate_faq.py --input my_questions.txt --output my_faq.md

# With custom title
python generate_faq.py --title "Product FAQ" --output product_faq.md
```

### Questions File Format

**Text file** (one question per line):
```
What is this product?
How do I get started?
What are the pricing options?
```

**JSON file**:
```json
["What is this product?", "How do I get started?", "What are the pricing options?"]
```

### Example
```bash
# Create a questions file
echo "What is Python?" > questions.txt
echo "How do I install Python?" >> questions.txt
echo "What are Python's main features?" >> questions.txt

# Generate FAQ
python generate_faq.py --input questions.txt --output python_faq.md
```

---

## Future Enhancements

- [x] **POST /crawl endpoint** - Crawl websites via API ✅
- [x] **Regenerate embeddings** - Re-index without re-crawling ✅
- [x] **FAQ Generator** - Generate FAQ documents automatically ✅
- [ ] Support for PDF documents
- [ ] Multi-language support
- [ ] Conversation history/context
- [ ] User authentication
- [ ] Rate limiting
- [ ] Caching for common questions
- [ ] Better error handling and logging
- [ ] Docker containerization
- [ ] Admin dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and development.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Open an issue on GitHub

## Acknowledgments

- OpenAI for embeddings and language models
- ChromaDB for vector storage
- FastAPI for the web framework
- BeautifulSoup for web scraping

---

Built with ❤️ for learning RAG systems

