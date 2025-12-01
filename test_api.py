"""
Test script for the RAG Support Bot API
"""
import requests
import json


def test_api(base_url: str = "http://localhost:8000"):
    """Test all API endpoints"""
    
    print("=" * 60)
    print("RAG Support Bot API - Test Suite")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n[Test 1] Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Root endpoint working")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test 2: Health check
    print("\n[Test 2] Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert "status" in data
        print("✓ Health endpoint working")
        
        if data.get("collection_count", 0) == 0:
            print("⚠ Warning: Vector store is empty. Run indexer first!")
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
    
    # Test 3: Stats endpoint
    print("\n[Test 3] Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Stats endpoint working")
    except Exception as e:
        print(f"✗ Stats endpoint failed: {e}")
    
    # Test 4: Ask endpoint - valid question
    print("\n[Test 4] Testing ask endpoint with valid question...")
    try:
        question = {
            "question": "What is this website about?",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/ask",
            json=question,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Question: {data['question']}")
            print(f"Answer: {data['answer'][:200]}...")
            print(f"Sources: {len(data['sources'])}")
            print(f"Context used: {data['context_used']}")
            print("✓ Ask endpoint working")
        else:
            print(f"Response: {response.json()}")
            if response.status_code == 400:
                print("⚠ Vector store is empty. Run indexer first!")
    except Exception as e:
        print(f"✗ Ask endpoint failed: {e}")
    
    # Test 5: Ask endpoint - invalid request
    print("\n[Test 5] Testing ask endpoint with invalid request...")
    try:
        response = requests.post(
            f"{base_url}/ask",
            json={"question": ""},  # Empty question
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 422  # Validation error
        print("✓ Validation working correctly")
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test RAG API')
    parser.add_argument(
        '--url',
        type=str,
        default="http://localhost:8000",
        help='Base URL of the API'
    )
    
    args = parser.parse_args()
    test_api(args.url)

