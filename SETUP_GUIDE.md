# Quick Setup Guide

## Step-by-Step Setup

### 1. Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd rag-support-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
# TARGET_WEBSITE=https://example.com
# MAX_PAGES=50
```

### 4. Index a Website

```bash
# Index your target website
python indexer.py --reset

# Or specify custom parameters
python indexer.py --url https://docs.python.org --max-pages 20 --reset
```

This will:
- Crawl the website
- Process and chunk the content
- Generate embeddings
- Store in vector database

### 5. Start the API Server

```bash
python main.py
```

The API will be available at: http://localhost:8000

### 6. Test the API

#### Using the browser
Visit http://localhost:8000/docs for interactive API documentation

#### Using curl
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is this about?\"}"
```

#### Using the test script
```bash
python test_api.py
```

#### Using the example client
```bash
python example_usage.py
```

## Common Commands

```bash
# Re-index with fresh data
python indexer.py --reset

# Use cached crawl data
python indexer.py --use-cached

# Index a different website
python indexer.py --url https://example.com --max-pages 30 --reset

# Start API server
python main.py

# Test the API
python test_api.py
```

## Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file configured with OpenAI API key
- [ ] Website indexed successfully
- [ ] API server running
- [ ] Successfully asked a test question

## Next Steps

1. Try asking different questions
2. Experiment with different websites
3. Adjust configuration parameters
4. Read the full README.md for advanced usage

## Troubleshooting

**API Key Error**: Make sure your OpenAI API key is in the .env file

**Empty Database**: Run `python indexer.py --reset` before starting the server

**Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

**Server Won't Start**: Check if port 8000 is already in use

