"""Check embedding generation status."""

import os
import psycopg2


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def check_status():
    """Check embedding generation status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN featured_image IS NOT NULL AND featured_image != '' THEN 1 END) as with_images,
                COUNT(CASE WHEN image_embedding IS NOT NULL THEN 1 END) as with_image_embeddings,
                COUNT(CASE WHEN text_embedding IS NOT NULL THEN 1 END) as with_text_embeddings,
                COUNT(CASE WHEN image_embedding IS NOT NULL AND text_embedding IS NOT NULL THEN 1 END) as with_both
            FROM products
        """)
        
        stats = cursor.fetchone()
        total, with_images, with_image_emb, with_text_emb, with_both = stats
        
        print("Embedding Generation Status:")
        print("=" * 50)
        print(f"Total products: {total}")
        print(f"Products with images: {with_images}")
        print(f"Products with image embeddings: {with_image_emb} ({with_image_emb/with_images*100:.1f}% of images)")
        print(f"Products with text embeddings: {with_text_emb} ({with_text_emb/total*100:.1f}% of total)")
        print(f"Products with both embeddings: {with_both} ({with_both/total*100:.1f}% of total)")
        
        if with_images > with_image_emb:
            remaining = with_images - with_image_emb
            print(f"\n⚠️  {remaining} products still need image embeddings")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    check_status()

