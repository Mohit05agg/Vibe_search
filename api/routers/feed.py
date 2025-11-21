"""
Feed endpoints for scraped images.
"""

from fastapi import APIRouter, HTTPException
from api.database import get_db_connection
from api.models import ScrapedImagesResponse, ScrapedImageResponse
from psycopg2.extras import RealDictCursor
import json

router = APIRouter()


@router.get("/scraped-images", response_model=ScrapedImagesResponse)
async def get_scraped_images(limit: int = 50):
    """
    Get scraped images for explore feed.
    Includes AI-processed metadata (detected class, colors, styles, brands, quality scores).
    """
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
                scraped_at,
                detected_class,
                bbox,
                extracted_colors,
                extracted_styles,
                extracted_brands,
                local_path,
                quality_score
            FROM scraped_images
            ORDER BY scraped_at DESC
            LIMIT %s
        """, (limit,))
        
        images = cursor.fetchall()
        
        # Convert to response format
        image_list = []
        for img in images:
            img_dict = dict(img)
            # Parse quality_score JSONB if present
            if img_dict.get('quality_score') and isinstance(img_dict['quality_score'], str):
                try:
                    img_dict['quality_score'] = json.loads(img_dict['quality_score'])
                except:
                    img_dict['quality_score'] = None
            # Convert scraped_at to string if datetime
            if img_dict.get('scraped_at'):
                img_dict['scraped_at'] = str(img_dict['scraped_at'])
            image_list.append(ScrapedImageResponse(**img_dict))
        
        return ScrapedImagesResponse(
            images=image_list,
            total=len(image_list)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

