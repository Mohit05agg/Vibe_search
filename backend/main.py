"""
FastAPI backend for Vibe Search.
Multimodal search engine API endpoints.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from backend.database import get_db_connection
from backend.search import image_search, text_search


app = FastAPI(
    title="Vibe Search API",
    description="Multimodal product search engine API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TextSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    colors: Optional[List[str]] = Field(None, description="Filter by colors")
    gender: Optional[str] = Field(None, description="Filter by gender")


class ProductResult(BaseModel):
    product_id: str
    title: str
    category: Optional[str]
    sub_category: Optional[str]
    brand_name: Optional[str]
    featured_image: Optional[str]
    lowest_price: Optional[float]
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    pdp_url: Optional[str]


class SearchResponse(BaseModel):
    results: List[ProductResult]
    total: int
    query: Optional[str] = None


class ImageSearchRequest(BaseModel):
    image_url: Optional[str] = Field(None, description="URL of image to search")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    colors: Optional[List[str]] = Field(None, description="Filter by colors")
    gender: Optional[str] = Field(None, description="Filter by gender")


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Vibe Search API",
        "version": "1.0.0",
        "endpoints": {
            "text_search": "/api/search/text",
            "image_search": "/api/search/image",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/api/search/text", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Text-based product search using natural language queries.
    
    Uses semantic embeddings and keyword matching to find relevant products.
    """
    try:
        results = text_search(
            query=request.query,
            limit=request.limit,
            category=request.category,
            brand=request.brand,
            min_price=request.min_price,
            max_price=request.max_price,
            colors=request.colors,
            gender=request.gender
        )
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/api/search/image", response_model=SearchResponse)
async def search_by_image(
    request: Optional[ImageSearchRequest] = None,
    file: Optional[UploadFile] = File(None)
):
    """
    Image-based product search using visual similarity.
    
    Accepts either:
    - Image file upload
    - Image URL in request body
    
    Returns visually similar products using CLIP embeddings.
    """
    try:
        # Handle image URL from request body
        image_url = None
        limit = 20
        filters = {}
        
        if request:
            image_url = request.image_url
            limit = request.limit
            filters = {
                "category": request.category,
                "brand": request.brand,
                "min_price": request.min_price,
                "max_price": request.max_price,
                "colors": request.colors,
                "gender": request.gender
            }
        
        # If file is uploaded, save temporarily and process
        if file:
            # For now, we'll use image_url approach
            # In production, you'd save the file and process it
            raise HTTPException(
                status_code=501,
                detail="File upload not yet implemented. Please use image_url parameter."
            )
        
        if not image_url:
            raise HTTPException(
                status_code=400,
                detail="Either image_url or file must be provided"
            )
        
        results = image_search(
            image_url=image_url,
            limit=limit,
            **filters
        )
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

