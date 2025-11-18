"""
Search functionality for multimodal product search.
Implements visual and text-based search using vector embeddings.
"""

import os
import io
from typing import List, Optional, Dict
import time

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

from backend.database import get_db_connection


# Model loading (lazy loading)
_clip_model = None
_clip_processor = None
_text_model = None


def get_clip_model():
    """Lazy load CLIP model."""
    global _clip_model, _clip_processor
    if _clip_model is None:
        print("Loading CLIP model...")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model.eval()
        if torch.cuda.is_available():
            _clip_model = _clip_model.cuda()
    return _clip_model, _clip_processor


def get_text_model():
    """Lazy load text model."""
    global _text_model
    if _text_model is None:
        print("Loading text model...")
        _text_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _text_model


def download_image(url: str, timeout: int = 10) -> Optional[Image.Image]:
    """Download image from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return None
        
        image = Image.open(io.BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception:
        return None


def build_filter_query(filters: Dict) -> tuple:
    """
    Build WHERE clause and parameters for filtering.
    
    Returns:
        (where_clause, params_dict)
    """
    conditions = []
    params = {}
    
    if filters.get("category"):
        conditions.append("category = %(category)s")
        params["category"] = filters["category"]
    
    if filters.get("brand"):
        conditions.append("brand_name = %(brand)s")
        params["brand"] = filters["brand"]
    
    if filters.get("min_price") is not None:
        conditions.append("lowest_price >= %(min_price)s")
        params["min_price"] = float(filters["min_price"])
    
    if filters.get("max_price") is not None:
        conditions.append("lowest_price <= %(max_price)s")
        params["max_price"] = float(filters["max_price"])
    
    if filters.get("colors"):
        # Check if any of the extracted colors match (using array overlap)
        conditions.append("extracted_colors && %(colors_array)s::text[]")
        params["colors_array"] = filters["colors"]
    
    if filters.get("gender"):
        conditions.append("gender = %(gender)s")
        params["gender"] = filters["gender"]
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, params


def image_search(
    image_url: str,
    limit: int = 20,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    colors: Optional[List[str]] = None,
    gender: Optional[str] = None
) -> List[Dict]:
    """
    Search products by image similarity using CLIP embeddings.
    
    Args:
        image_url: URL of the query image
        limit: Number of results to return
        category: Filter by category
        brand: Filter by brand
        min_price: Minimum price filter
        max_price: Maximum price filter
        colors: List of colors to filter by
        gender: Filter by gender
        
    Returns:
        List of product dictionaries with similarity scores
    """
    # Download and process query image
    image = download_image(image_url)
    if image is None:
        return []
    
    # Generate query embedding
    model, processor = get_clip_model()
    
    with torch.no_grad():
        inputs = processor(images=image, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        query_embedding = model.get_image_features(**inputs)
        query_embedding = query_embedding / query_embedding.norm(dim=-1, keepdim=True)
        query_vector = query_embedding[0].cpu().numpy().tolist()
    
    # Build filter conditions
    filters = {
        "category": category,
        "brand": brand,
        "min_price": min_price,
        "max_price": max_price,
        "colors": colors,
        "gender": gender
    }
    where_clause, params = build_filter_query(filters)
    
    # Search in database using cosine similarity
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"""
            SELECT 
                product_id,
                title,
                category,
                sub_category,
                brand_name,
                featured_image,
                lowest_price,
                pdp_url,
                1 - (image_embedding <=> %(query_vector)s::vector) as similarity_score
            FROM products
            WHERE image_embedding IS NOT NULL
            AND {where_clause}
            AND is_active = TRUE
            ORDER BY image_embedding <=> %(query_vector)s::vector
            LIMIT %(limit)s
        """
        
        params["query_vector"] = query_vector
        params["limit"] = limit
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dicts
        products = []
        for row in results:
            products.append({
                "product_id": row["product_id"],
                "title": row["title"],
                "category": row["category"],
                "sub_category": row["sub_category"],
                "brand_name": row["brand_name"],
                "featured_image": row["featured_image"],
                "lowest_price": float(row["lowest_price"]) if row["lowest_price"] else None,
                "similarity_score": float(row["similarity_score"]),
                "pdp_url": row["pdp_url"]
            })
        
        return products
        
    finally:
        cursor.close()
        conn.close()


def text_search(
    query: str,
    limit: int = 20,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    colors: Optional[List[str]] = None,
    gender: Optional[str] = None
) -> List[Dict]:
    """
    Search products by text query using semantic embeddings.
    
    Args:
        query: Natural language search query
        limit: Number of results to return
        category: Filter by category
        brand: Filter by brand
        min_price: Minimum price filter
        max_price: Maximum price filter
        colors: List of colors to filter by
        gender: Filter by gender
        
    Returns:
        List of product dictionaries with similarity scores
    """
    # Generate query embedding
    model = get_text_model()
    query_embedding = model.encode(query, normalize_embeddings=True)
    query_vector = query_embedding.tolist()
    
    # Build filter conditions
    filters = {
        "category": category,
        "brand": brand,
        "min_price": min_price,
        "max_price": max_price,
        "colors": colors,
        "gender": gender
    }
    where_clause, params = build_filter_query(filters)
    
    # Search in database using cosine similarity
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"""
            SELECT 
                product_id,
                title,
                category,
                sub_category,
                brand_name,
                featured_image,
                lowest_price,
                pdp_url,
                1 - (text_embedding <=> %(query_vector)s::vector) as similarity_score
            FROM products
            WHERE text_embedding IS NOT NULL
            AND {where_clause}
            AND is_active = TRUE
            ORDER BY text_embedding <=> %(query_vector)s::vector
            LIMIT %(limit)s
        """
        
        params["query_vector"] = query_vector
        params["limit"] = limit
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dicts
        products = []
        for row in results:
            products.append({
                "product_id": row["product_id"],
                "title": row["title"],
                "category": row["category"],
                "sub_category": row["sub_category"],
                "brand_name": row["brand_name"],
                "featured_image": row["featured_image"],
                "lowest_price": float(row["lowest_price"]) if row["lowest_price"] else None,
                "similarity_score": float(row["similarity_score"]),
                "pdp_url": row["pdp_url"]
            })
        
        return products
        
    finally:
        cursor.close()
        conn.close()

