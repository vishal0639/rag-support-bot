# Quick Start Guide - RAG Support Bot

**Get started in 3 minutes!** ⚡

---

## Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

---

## Installation

```bash
# 1. Clone or download the project
cd rag-support-bot

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
copy .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here
```

---

## Usage - Method 1: API-First (Recommended)

### Step 1: Start the API Server
```bash
python main.py
```

Output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Crawl a Website
Open a new terminal and run:

```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d "{\"base_url\": \"https://docs.python.org/3/tutorial\", \"max_pages\": 10, \"reset\": true}"
```

**Or use Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/crawl",
    json={
        "base_url": "https://docs.python.org/3/tutorial",
        "max_pages": 10,
        "reset": True
    }
)
print(response.json())
```

### Step 3: Ask Questions
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is Python?\"}"
```

**Or use Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "What is Python?"}
)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

---

## Usage - Method 2: CLI-First

### Step 1: Index a Website
```bash
python indexer.py --url https://docs.python.org/3/tutorial --max-pages 10 --reset
```

Wait for indexing to complete (~1-2 minutes for 10 pages).

### Step 2: Start the API
```bash
python main.py
```

### Step 3: Ask Questions
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is Python?\"}"
```

---

## Interactive API Documentation

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser!

---

## All Available Endpoints

### 1. Crawl a Website
```bash
POST /crawl
Body: {"base_url": "https://example.com", "max_pages": 50, "reset": false}
```

### 2. Ask a Question
```bash
POST /ask
Body: {"question": "Your question?", "top_k": 5}
```

### 3. Regenerate Embeddings
```bash
POST /regenerate
Body: (none - uses cached data)
```

### 4. Health Check
```bash
GET /health
```

### 5. Statistics
```bash
GET /stats
```

---

## Generate FAQ Document

```bash
# Use default questions
python generate_faq.py

# Use custom questions
python generate_faq.py --input questions.txt --output my_faq.md

# With custom title
python generate_faq.py --title "My Product FAQ"
```

---

## Example Questions to Try

Depending on what website you crawled, try questions like:

**For Python docs:**
- "What is Python?"
- "How do I install Python?"
- "What are Python's main features?"
- "How do I create a function in Python?"

**For product documentation:**
- "What is this product?"
- "How do I get started?"
- "What are the pricing options?"
- "Is there a free trial?"

---

## Troubleshooting

### "Vector store is empty"
**Solution:** Run the crawler first:
```bash
# Option 1: Via API
curl -X POST http://localhost:8000/crawl -H "Content-Type: application/json" -d '{"base_url": "https://example.com"}'

# Option 2: Via CLI
python indexer.py --url https://example.com --reset
```

### "OpenAI API key not found"
**Solution:** Check your `.env` file has:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Crawler gets blocked
**Solution:** Increase delay in `config.py`:
```python
REQUEST_DELAY = 1.0  # Increase from 0.5 to 1.0 seconds
```

### Out of memory
**Solution:** Reduce pages:
```python
MAX_PAGES = 20  # Reduce from 50
```

---

## Configuration

Edit `config.py` or use `.env` file:

```python
# Crawling
TARGET_WEBSITE = "https://example.com"
MAX_PAGES = 50
REQUEST_DELAY = 0.5

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Models
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"

# Retrieval
TOP_K_RESULTS = 5
```

---

## Cost Estimate

**One-time indexing (50 pages):** ~$0.10 - $0.50
**Per question:** ~$0.001 - $0.01

**Monthly estimate (1000 questions):** ~$2-10

---

## Next Steps

1. ✅ Crawl a website
2. ✅ Ask questions
3. 🚀 Deploy to production
4. 📊 Monitor usage and costs
5. 🔧 Customize for your use case

---

## Full Documentation

- **README.md** - Complete guide with all features
- **SETUP_GUIDE.md** - Detailed setup instructions
- **TESTING.md** - Testing scenarios and examples
- **PROJECT_REVIEW.md** - Project assessment and recommendations
- **IMPLEMENTATION_PLAN.md** - Technical architecture and design

---

## Support

- Check `/docs` endpoint for API documentation
- Review troubleshooting section above
- See examples in `example_usage.py`

---

**Happy building!** 🎉

*Built with FastAPI, OpenAI, and ChromaDB*

