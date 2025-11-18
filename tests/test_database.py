"""
Database testing script.
Verifies database setup and data integrity.
"""

import os
import psycopg2


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "vibe_search"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        conn = get_db_connection()
        conn.close()
        print("OK Database connection successful")
        return True
    except Exception as e:
        print(f"X Database connection failed: {e}")
        return False


def test_pgvector():
    """Test pgvector extension."""
    print("\nTesting pgvector extension...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        result = cursor.fetchone()
        
        if result:
            print("OK pgvector extension is installed")
            return True
        else:
            print("X pgvector extension not found")
            return False
    except Exception as e:
        print(f"X Error checking pgvector: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def test_tables():
    """Test if required tables exist."""
    print("\nTesting database tables...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    required_tables = ['products', 'scraped_images']
    missing_tables = []
    
    try:
        for table in required_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print(f"OK Table '{table}' exists")
            else:
                print(f"X Table '{table}' not found")
                missing_tables.append(table)
        
        return len(missing_tables) == 0
    except Exception as e:
        print(f"X Error checking tables: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def test_products():
    """Test products data."""
    print("\nTesting products data...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        print(f"OK Total products: {total}")
        
        # Check products with embeddings
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE image_embedding IS NOT NULL) as with_image_emb,
                COUNT(*) FILTER (WHERE text_embedding IS NOT NULL) as with_text_emb
            FROM products
        """)
        image_emb, text_emb = cursor.fetchone()
        
        print(f"OK Products with image embeddings: {image_emb}")
        print(f"OK Products with text embeddings: {text_emb}")
        
        # Check metadata extraction
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE array_length(extracted_colors, 1) > 0) as with_colors,
                COUNT(*) FILTER (WHERE array_length(extracted_styles, 1) > 0) as with_styles
            FROM products
        """)
        with_colors, with_styles = cursor.fetchone()
        
        print(f"OK Products with extracted colors: {with_colors}")
        print(f"OK Products with extracted styles: {with_styles}")
        
        return total > 0
    except Exception as e:
        print(f"X Error checking products: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def test_scraped_images():
    """Test scraped images data."""
    print("\nTesting scraped images data...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM scraped_images")
        total = cursor.fetchone()[0]
        print(f"OK Total scraped images: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT source, COUNT(*) 
                FROM scraped_images 
                GROUP BY source
            """)
            sources = cursor.fetchall()
            for source, count in sources:
                print(f"  - {source}: {count} images")
        
        return True
    except Exception as e:
        print(f"X Error checking scraped images: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def test_vector_search():
    """Test vector similarity search."""
    print("\nTesting vector similarity search...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Test image embedding search
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE image_embedding IS NOT NULL
            LIMIT 1
        """)
        has_image_emb = cursor.fetchone()[0] > 0
        
        if has_image_emb:
            # Try a simple vector query
            cursor.execute("""
                SELECT id, title
                FROM products
                WHERE image_embedding IS NOT NULL
                ORDER BY image_embedding <=> (
                    SELECT image_embedding 
                    FROM products 
                    WHERE image_embedding IS NOT NULL 
                    LIMIT 1
                )
                LIMIT 5
            """)
            results = cursor.fetchall()
            print(f"OK Vector search test: Found {len(results)} similar products")
            return True
        else:
            print("WARNING: No image embeddings found, skipping vector search test")
            return True
    except Exception as e:
        print(f"X Error testing vector search: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def main():
    """Run all database tests."""
    print("=" * 60)
    print("Database Test Suite")
    print("=" * 60)
    
    tests = [
        test_connection,
        test_pgvector,
        test_tables,
        test_products,
        test_scraped_images,
        test_vector_search,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"X Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()

