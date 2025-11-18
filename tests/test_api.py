"""
API testing script.
Tests all endpoints and measures performance.
"""

import requests
import time
import json
from typing import Dict, List

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /api/health...")
    response = requests.get(f"{API_URL}/api/health")
    assert response.status_code == 200
    print(f"✓ Health check passed: {response.json()}")
    return True


def test_text_search():
    """Test text search endpoint."""
    print("\nTesting /api/search/text...")
    
    test_queries = [
        "black sneakers",
        "summer dress",
        "luxury watch",
    ]
    
    for query in test_queries:
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/search/text",
            json={"query": query, "limit": 5}
        )
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Query '{query}': {data['total']} results in {data['query_time_ms']:.2f}ms")
        
        # Check response time
        if elapsed > 500:
            print(f"  ⚠️  Response time ({elapsed:.2f}ms) exceeds 500ms target")
    
    return True


def test_image_search():
    """Test image search endpoint."""
    print("\nTesting /api/search/image...")
    
    # Use a product image URL from the database
    test_image_url = "https://images.stockx.com/images/Nike-Air-Max-90-Black-White.jpg"
    
    start = time.time()
    response = requests.post(
        f"{API_URL}/api/search/image",
        json={"image_url": test_image_url, "limit": 5}
    )
    elapsed = (time.time() - start) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Image search: {data['total']} results in {data['query_time_ms']:.2f}ms")
        
        if elapsed > 500:
            print(f"  ⚠️  Response time ({elapsed:.2f}ms) exceeds 500ms target")
        return True
    else:
        print(f"✗ Image search failed: {response.status_code}")
        return False


def test_feed_endpoint():
    """Test scraped images feed endpoint."""
    print("\nTesting /api/scraped-images...")
    
    response = requests.get(f"{API_URL}/api/scraped-images?limit=10")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Feed endpoint: {data['total']} images")
    return True


def performance_test():
    """Run performance tests."""
    print("\n" + "=" * 60)
    print("Performance Testing")
    print("=" * 60)
    
    queries = ["black sneakers", "summer dress", "luxury watch"]
    times = []
    
    for query in queries:
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/search/text",
            json={"query": query, "limit": 20}
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        if response.status_code == 200:
            print(f"Query '{query}': {elapsed:.2f}ms")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\nAverage response time: {avg_time:.2f}ms")
    print(f"Max response time: {max_time:.2f}ms")
    
    if avg_time < 500:
        print("✓ Average response time meets <500ms target")
    else:
        print(f"⚠️  Average response time ({avg_time:.2f}ms) exceeds 500ms target")
    
    return avg_time < 500


def main():
    """Run all tests."""
    print("=" * 60)
    print("Vibe Search API Test Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        test_text_search()
        test_image_search()
        test_feed_endpoint()
        
        # Performance test
        performance_test()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API")
        print("Make sure the server is running: python run_server.py")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()

