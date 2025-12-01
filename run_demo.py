"""
Demo script - Full RAG Support Bot demonstration
This script shows the complete workflow from indexing to querying
"""
import subprocess
import sys
import time
import requests
import json
from pathlib import Path


def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\nPlease create a .env file with your OpenAI API key:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your OpenAI API key")
        print("\nExample:")
        print("  OPENAI_API_KEY=sk-your-key-here")
        print("  TARGET_WEBSITE=https://example.com")
        print("  MAX_PAGES=5")
        return False
    
    # Check if API key exists
    with open(env_file, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' not in content or 'sk-' not in content:
            print("⚠️  Warning: OPENAI_API_KEY not found in .env file")
            print("Please add your OpenAI API key to continue")
            return False
    
    print("✅ .env file found and configured")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import chromadb
        import bs4
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install requirements:")
        print("  pip install -r requirements.txt")
        return False


def run_indexing():
    """Run the indexing process"""
    print("\n" + "="*60)
    print("STEP 1: INDEXING")
    print("="*60)
    print("\nIndexing a demo website (https://example.com)...")
    print("This will take a few moments...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'indexer.py', '--url', 'https://example.com', '--max-pages', '2', '--reset'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Indexing completed successfully!")
            return True
        else:
            print("\n❌ Indexing failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        return False


def start_server():
    """Start the API server in background"""
    print("\n" + "="*60)
    print("STEP 2: STARTING API SERVER")
    print("="*60)
    print("\nStarting FastAPI server...")
    
    try:
        # Start server as subprocess
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("Waiting for server to start", end="")
        for _ in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("\n✅ Server started successfully!")
                    print("🌐 API available at: http://localhost:8000")
                    print("📚 Documentation at: http://localhost:8000/docs")
                    return process
            except:
                continue
        
        print("\n⚠️  Server might not be ready yet, but continuing...")
        return process
        
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return None


def test_queries(server_process):
    """Test the API with sample queries"""
    print("\n" + "="*60)
    print("STEP 3: TESTING QUERIES")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n[Test 1] Health Check")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/health")
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Indexed chunks: {data['collection_count']}")
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Ask a question
    print("\n[Test 2] Ask Question")
    print("-" * 40)
    question = "What is this website about?"
    print(f"Question: {question}")
    
    try:
        response = requests.post(
            f"{base_url}/ask",
            json={"question": question, "top_k": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAnswer: {data['answer']}\n")
            
            if data['sources']:
                print("Sources:")
                for i, source in enumerate(data['sources'], 1):
                    print(f"  {i}. {source['title']}")
                    print(f"     {source['url']}")
            
            print(f"\n✅ Query successful (used {data['context_used']} chunks)")
        else:
            print(f"❌ Query failed with status {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test 3: Another question
    print("\n[Test 3] Another Question")
    print("-" * 40)
    question2 = "How can I use this website?"
    print(f"Question: {question2}")
    
    try:
        response = requests.post(
            f"{base_url}/ask",
            json={"question": question2, "top_k": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAnswer: {data['answer']}\n")
            print(f"✅ Query successful")
        else:
            print(f"⚠️  Query returned status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Query failed: {e}")


def cleanup(server_process):
    """Stop the server"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    if server_process:
        print("\nStopping API server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Server stopped")


def main():
    """Run complete demo"""
    print("="*60)
    print("RAG SUPPORT BOT - COMPLETE DEMO")
    print("="*60)
    
    # Pre-flight checks
    print("\n📋 Pre-flight Checks")
    print("-" * 40)
    
    if not check_dependencies():
        return
    
    if not check_env_file():
        return
    
    # Run the demo
    server_process = None
    
    try:
        # Step 1: Index
        if not run_indexing():
            print("\n❌ Demo failed at indexing step")
            return
        
        # Step 2: Start server
        server_process = start_server()
        if not server_process:
            print("\n❌ Demo failed at server startup")
            return
        
        # Step 3: Test queries
        test_queries(server_process)
        
        # Success!
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nThe server is still running. You can:")
        print("  1. Visit http://localhost:8000/docs for API documentation")
        print("  2. Run: python test_api.py for more tests")
        print("  3. Run: python example_usage.py for example usage")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep server running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n\nStopping server...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    finally:
        # Cleanup
        if server_process:
            cleanup(server_process)
    
    print("\n" + "="*60)
    print("Thank you for trying RAG Support Bot!")
    print("="*60)


if __name__ == "__main__":
    main()

