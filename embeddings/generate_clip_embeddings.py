"""
Generate CLIP embeddings for product images.
Downloads images, processes them, and stores 512-dimensional embeddings.
"""

import os
import io
from pathlib import Path
from typing import Optional, List
import time

import requests
import psycopg2
from psycopg2.extras import execute_batch
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm


# CLIP model configuration
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"  # 512-dimensional embeddings
EMBEDDING_DIM = 512

# Image download settings
MAX_IMAGE_SIZE = (224, 224)  # CLIP input size
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def download_image(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[Image.Image]:
    """
    Download image from URL.
    
    Args:
        url: Image URL
        timeout: Request timeout in seconds
        
    Returns:
        PIL Image or None if download fails
    """
    if not url or not url.strip():
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return None
            
            # Load image
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)  # Wait before retry
                continue
            return None
    
    return None


def generate_clip_embedding(image: Image.Image, model, processor) -> Optional[List[float]]:
    """
    Generate CLIP embedding for an image.
    
    Args:
        image: PIL Image
        model: CLIP model
        processor: CLIP processor
        
    Returns:
        512-dimensional embedding vector or None
    """
    try:
        # Process image
        inputs = processor(images=image, return_tensors="pt")
        
        # Generate embedding
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
            # Normalize the embedding
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            embedding = image_features[0].cpu().numpy().tolist()
        
        return embedding
        
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def process_products_batch(
    products: List[tuple],
    model,
    processor,
    cursor,
    batch_size: int = 10
):
    """
    Process a batch of products and generate embeddings.
    
    Args:
        products: List of (id, product_id, image_url) tuples
        model: CLIP model
        processor: CLIP processor
        cursor: Database cursor
        batch_size: Number of products to process before committing
    """
    updates = []
    processed = 0
    failed = 0
    
    for product_id, db_product_id, image_url in tqdm(products, desc="Processing images"):
        # Download image
        image = download_image(image_url)
        
        if image is None:
            failed += 1
            continue
        
        # Generate embedding
        embedding = generate_clip_embedding(image, model, processor)
        
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
    """Update embeddings for a batch of products."""
    update_query = """
        UPDATE products
        SET image_embedding = %s::vector
        WHERE id = %s
    """
    
    execute_batch(cursor, update_query, updates)


def generate_all_embeddings(batch_size: int = 10, limit: Optional[int] = None):
    """
    Generate CLIP embeddings for all products with images.
    
    Args:
        batch_size: Number of products to process before committing
        limit: Optional limit on number of products to process (for testing)
    """
    print("Loading CLIP model...")
    print(f"Model: {CLIP_MODEL_NAME}")
    
    # Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    model.to(device)
    model.eval()
    
    print("Model loaded successfully!")
    print("-" * 50)
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get products with images but no embeddings yet
        query = """
            SELECT id, product_id, featured_image
            FROM products
            WHERE featured_image IS NOT NULL
            AND featured_image != ''
            AND image_embedding IS NULL
            ORDER BY id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        products = cursor.fetchall()
        
        total = len(products)
        print(f"Found {total} products to process")
        
        if total == 0:
            print("No products need embeddings!")
            return
        
        # Process products
        processed, failed = process_products_batch(
            products, model, processor, cursor, batch_size
        )
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print("Embedding Generation Summary:")
        print(f"  Total products: {total}")
        print(f"  Successfully processed: {processed}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {processed/total*100:.1f}%")
        
        # Verify embeddings
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE image_embedding IS NOT NULL
        """)
        with_embeddings = cursor.fetchone()[0]
        print(f"\nTotal products with embeddings: {with_embeddings}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error generating embeddings: {e}")
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
    
    print("Starting CLIP embedding generation...")
    print("=" * 50)
    
    generate_all_embeddings(batch_size=10, limit=limit)
    
    print("\nEmbedding generation completed!")

