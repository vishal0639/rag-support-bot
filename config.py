"""
Configuration settings for the RAG Support Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"

# Crawling Configuration
TARGET_WEBSITE = os.getenv("TARGET_WEBSITE", "https://example.com")
MAX_PAGES = int(os.getenv("MAX_PAGES", "50"))
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 0.5  # Delay between requests in seconds

# Chunking Configuration
CHUNK_SIZE = 500  # Number of tokens per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "website_content"

# Retrieval Configuration
TOP_K_RESULTS = 5  # Number of similar chunks to retrieve

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

