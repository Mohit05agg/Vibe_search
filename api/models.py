"""
Pydantic models for request/response schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    """Product response model."""
    id: int
    product_id: str
    title: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    brand_name: Optional[str] = None
    featured_image: Optional[str] = None
    lowest_price: Optional[float] = None
    pdp_url: Optional[str] = None
    similarity_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response model."""
    products: List[ProductResponse]
    total: int
    query_time_ms: float


class ImageSearchRequest(BaseModel):
    """Image search request model."""
    image_url: Optional[str] = Field(None, description="URL of the image to search")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    colors: Optional[List[str]] = Field(None, description="Filter by colors")
    gender: Optional[str] = Field(None, description="Filter by gender")


class TextSearchRequest(BaseModel):
    """Text search request model."""
    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    colors: Optional[List[str]] = Field(None, description="Filter by colors")
    gender: Optional[str] = Field(None, description="Filter by gender")


class ScrapedImageResponse(BaseModel):
    """Scraped image response model with AI-processed data."""
    id: int
    source: str
    source_url: str
    image_url: str
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    engagement_count: int = 0
    username: Optional[str] = None
    board_name: Optional[str] = None
    scraped_at: Optional[str] = None
    # AI-processed fields
    detected_class: Optional[str] = None
    bbox: Optional[List[int]] = None
    extracted_colors: Optional[List[str]] = None
    extracted_styles: Optional[List[str]] = None
    extracted_brands: Optional[List[str]] = None
    local_path: Optional[str] = None
    quality_score: Optional[dict] = None
    
    class Config:
        from_attributes = True


class ScrapedImagesResponse(BaseModel):
    """Response model for scraped images list."""
    images: List[ScrapedImageResponse]
    total: int

