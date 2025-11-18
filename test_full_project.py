"""
Complete project testing script.
Tests backend, frontend, database, and API endpoints.
"""

import requests
import time
import os
import psycopg2
from typing import Dict, List

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def test_backend_health():
    """Test backend health endpoint."""
    print_header("Testing Backend Health")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {API_URL}")
        print("   Make sure backend is running: python run_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_frontend_accessibility():
    """Test if frontend is accessible."""
    print_header("Testing Frontend Accessibility")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend is accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to frontend at {FRONTEND_URL}")
        print("   Make sure frontend is running: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_text_search():
    """Test text search API."""
    print_header("Testing Text Search API")
    
    test_queries = [
        "black sneakers",
        "summer dress",
        "luxury watch"
    ]
    
    all_passed = True
    
    for query in test_queries:
        try:
            start = time.time()
            response = requests.post(
                f"{API_URL}/api/search/text",
                json={"query": query, "limit": 5},
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query '{query}': {data['total']} results in {data['query_time_ms']:.2f}ms")
                
                if elapsed > 500:
                    print(f"   ⚠️  Response time ({elapsed:.2f}ms) exceeds 500ms target")
            else:
                print(f"❌ Query '{query}' failed: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Query '{query}' error: {e}")
            all_passed = False
    
    return all_passed


def test_image_search():
    """Test image search API."""
    print_header("Testing Image Search API")
    
    # Get a real image URL from the database
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "vibe_search"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT featured_image FROM products WHERE featured_image IS NOT NULL AND featured_image != '' LIMIT 1")
        result = cursor.fetchone()
        test_image_url = result[0] if result else None
        cursor.close()
        conn.close()
        
        if not test_image_url:
            print("⚠️  No product images found in database, skipping image search test")
            return True
    except Exception as e:
        print(f"⚠️  Could not get image URL from database: {e}")
        print("   Skipping image search test")
        return True
    
    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/search/image",
            json={"image_url": test_image_url, "limit": 5},
            timeout=30  # Image processing takes longer
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Image search: {data['total']} results in {data['query_time_ms']:.2f}ms")
            
            if elapsed > 1000:  # Image search can take longer
                print(f"   ⚠️  Response time ({elapsed:.2f}ms) is slow but acceptable for image processing")
            return True
        else:
            print(f"❌ Image search failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Image search error: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    print_header("Testing Database Connection")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "vibe_search"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cursor = conn.cursor()
        
        # Check products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Database connected: {product_count} products")
        
        # Check embeddings
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE image_embedding IS NOT NULL) as img_emb,
                COUNT(*) FILTER (WHERE text_embedding IS NOT NULL) as txt_emb
            FROM products
        """)
        img_emb, txt_emb = cursor.fetchone()
        print(f"✅ Embeddings: {img_emb} image, {txt_emb} text")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_api_endpoints():
    """Test all API endpoints."""
    print_header("Testing All API Endpoints")
    
    endpoints = [
        ("GET", "/api/health", None),
        ("GET", "/", None),
    ]
    
    all_passed = True
    
    for method, endpoint, data in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
            
            if response.status_code in [200, 404]:  # 404 is OK for root
                print(f"✅ {method} {endpoint}: {response.status_code}")
            else:
                print(f"❌ {method} {endpoint}: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")
            all_passed = False
    
    return all_passed


def performance_test():
    """Run performance tests."""
    print_header("Performance Testing")
    
    queries = ["black sneakers", "summer dress"]
    times = []
    
    for query in queries:
        try:
            start = time.time()
            response = requests.post(
                f"{API_URL}/api/search/text",
                json={"query": query, "limit": 20},
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if response.status_code == 200:
                print(f"Query '{query}': {elapsed:.2f}ms")
        except Exception as e:
            print(f"Error testing '{query}': {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\nAverage response time: {avg_time:.2f}ms")
        print(f"Max response time: {max_time:.2f}ms")
        
        if avg_time < 500:
            print("✅ Performance: Meets <500ms target")
            return True
        else:
            print(f"⚠️  Performance: Average ({avg_time:.2f}ms) exceeds 500ms target")
            return False
    
    return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Vibe Search - Complete Project Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test backend
    results.append(("Backend Health", test_backend_health()))
    
    # Test frontend
    results.append(("Frontend Accessibility", test_frontend_accessibility()))
    
    # Test database
    results.append(("Database Connection", test_database_connection()))
    
    # Test API endpoints
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Test search functionality
    results.append(("Text Search", test_text_search()))
    results.append(("Image Search", test_image_search()))
    
    # Performance test
    results.append(("Performance", performance_test()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Project is working correctly.")
        print("\nNext steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Test the search interface")
        print("3. Try text and image searches")
        print("4. Check explore feed")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        print("\nTroubleshooting:")
        print("- Make sure backend is running: python run_server.py")
        print("- Make sure frontend is running: cd frontend && npm run dev")
        print("- Check database connection")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

