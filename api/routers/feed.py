"""
Feed endpoints for scraped images.
"""

from fastapi import APIRouter, HTTPException
from api.database import get_db_connection
from psycopg2.extras import RealDictCursor

router = APIRouter()


@router.get("/scraped-images")
async def get_scraped_images(limit: int = 50):
    """Get scraped images for explore feed."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                id,
                source,
                source_url,
                image_url,
                caption,
                hashtags,
                engagement_count,
                username,
                board_name,
                scraped_at
            FROM scraped_images
            ORDER BY scraped_at DESC
            LIMIT %s
        """, (limit,))
        
        images = cursor.fetchall()
        
        return {
            "images": [dict(img) for img in images],
            "total": len(images)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

