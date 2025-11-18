"""
Generate text embeddings for product titles and descriptions.
Uses sentence-transformers (all-MiniLM-L6-v2) for 384-dimensional embeddings.
"""

import os
from typing import Optional, List

import psycopg2
from psycopg2.extras import execute_batch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# Sentence transformer model (384-dimensional embeddings)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def generate_text_embedding(text: str, model) -> Optional[List[float]]:
    """
    Generate text embedding for product title/description.
    
    Args:
        text: Product title or description
        model: Sentence transformer model
        
    Returns:
        384-dimensional embedding vector or None
    """
    if not text or not text.strip():
        return None
    
    try:
        # Generate embedding
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
        
    except Exception as e:
        print(f"Error generating text embedding: {e}")
        return None


def process_products_batch(products: List[tuple], model, cursor, batch_size: int = 50):
    """
    Process a batch of products and generate text embeddings.
    
    Args:
        products: List of (id, title, description) tuples
        model: Sentence transformer model
        cursor: Database cursor
        batch_size: Number of products to process before committing
    """
    updates = []
    processed = 0
    failed = 0
    
    for product_id, title, description in tqdm(products, desc="Processing text"):
        # Combine title and description
        text = title
        if description and description.strip():
            text = f"{title} {description}"
        
        # Generate embedding
        embedding = generate_text_embedding(text, model)
        
        if embedding is None:
            failed += 1
            continue
        
        # Store update
        updates.append((embedding, product_id))
        processed += 1
        
        # Commit in batches
        if len(updates) >= batch_size:
            _update_embeddings_batch(cursor, updates)
            updates = []
    
    # Process remaining
    if updates:
        _update_embeddings_batch(cursor, updates)
    
    return processed, failed


def _update_embeddings_batch(cursor, updates: List[tuple]):
    """Update text embeddings for a batch of products."""
    update_query = """
        UPDATE products
        SET text_embedding = %s::vector
        WHERE id = %s
    """
    
    execute_batch(cursor, update_query, updates)


def generate_all_text_embeddings(batch_size: int = 50, limit: Optional[int] = None):
    """
    Generate text embeddings for all products.
    
    Args:
        batch_size: Number of products to process before committing
        limit: Optional limit on number of products to process (for testing)
    """
    print("Loading sentence transformer model...")
    print(f"Model: {MODEL_NAME}")
    
    # Load model
    model = SentenceTransformer(MODEL_NAME)
    
    print("Model loaded successfully!")
    print("-" * 50)
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get products without text embeddings
        query = """
            SELECT id, title, description
            FROM products
            WHERE title IS NOT NULL
            AND title != ''
            AND text_embedding IS NULL
            ORDER BY id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        products = cursor.fetchall()
        
        total = len(products)
        print(f"Found {total} products to process")
        
        if total == 0:
            print("No products need text embeddings!")
            return
        
        # Process products
        processed, failed = process_products_batch(products, model, cursor, batch_size)
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print("Text Embedding Generation Summary:")
        print(f"  Total products: {total}")
        print(f"  Successfully processed: {processed}")
        print(f"  Failed: {failed}")
        if total > 0:
            print(f"  Success rate: {processed/total*100:.1f}%")
        
        # Verify embeddings
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE text_embedding IS NOT NULL
        """)
        with_embeddings = cursor.fetchone()[0]
        print(f"\nTotal products with text embeddings: {with_embeddings}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error generating text embeddings: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import sys
    
    # Allow limiting for testing
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"Processing limited to {limit} products (for testing)")
        except ValueError:
            pass
    
    print("Starting text embedding generation...")
    print("=" * 50)
    
    generate_all_text_embeddings(batch_size=50, limit=limit)
    
    print("\nText embedding generation completed!")

