"""
Search endpoints for image and text search.
"""

import time
import io
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

from api.models import (
    ImageSearchRequest, TextSearchRequest, SearchResponse, ProductResponse
)
from api.database import get_db_connection
from api.search_utils import build_filter_query, execute_vector_search

router = APIRouter()

# Load models (lazy loading on first request)
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
        print("Loading sentence transformer model...")
        _text_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _text_model


@router.post("/image", response_model=SearchResponse)
async def search_by_image(request: ImageSearchRequest):
    """
    Search products by image URL.
    
    Accepts an image URL and returns visually similar products using CLIP embeddings.
    """
    start_time = time.time()
    
    if not request.image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    
    # Download image from URL
    import requests
    try:
        response = requests.get(request.image_url, timeout=10)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
    
    # Generate embedding
    model, processor = get_clip_model()
    inputs = processor(images=image, return_tensors="pt")
    
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        query_embedding = image_features[0].cpu().numpy().tolist()
    
    # Build filter conditions
    filter_conditions = build_filter_query(
        category=request.category,
        brand=request.brand,
        min_price=request.min_price,
        max_price=request.max_price,
        colors=request.colors,
        gender=request.gender
    )
    
    # Execute vector search
    conn = get_db_connection()
    try:
        products = execute_vector_search(
            conn=conn,
            query_embedding=query_embedding,
            embedding_column="image_embedding",
            limit=request.limit,
            filter_conditions=filter_conditions
        )
        
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            products=[ProductResponse(**dict(p)) for p in products],
            total=len(products),
            query_time_ms=round(query_time, 2)
        )
    finally:
        conn.close()


@router.post("/image/upload", response_model=SearchResponse)
async def search_by_image_upload(
    image_file: UploadFile = File(...),
    limit: int = Form(20),
    category: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    min_price: Optional[float] = Form(None),
    max_price: Optional[float] = Form(None),
    colors: Optional[str] = Form(None),
    gender: Optional[str] = Form(None)
):
    """
    Search products by uploaded image file.
    
    Accepts an uploaded image file and returns visually similar products.
    """
    start_time = time.time()
    
    # Read uploaded file
    contents = await image_file.read()
    try:
        image = Image.open(io.BytesIO(contents))
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Generate embedding
    model, processor = get_clip_model()
    inputs = processor(images=image, return_tensors="pt")
    
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        query_embedding = image_features[0].cpu().numpy().tolist()
    
    # Parse colors filter
    color_list = None
    if colors:
        color_list = [c.strip() for c in colors.split(",") if c.strip()]
    
    # Build filter conditions
    filter_conditions = build_filter_query(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        colors=color_list,
        gender=gender
    )
    
    # Execute vector search
    conn = get_db_connection()
    try:
        products = execute_vector_search(
            conn=conn,
            query_embedding=query_embedding,
            embedding_column="image_embedding",
            limit=limit,
            filter_conditions=filter_conditions
        )
        
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            products=[ProductResponse(**dict(p)) for p in products],
            total=len(products),
            query_time_ms=round(query_time, 2)
        )
    finally:
        conn.close()


@router.post("/text", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Search products by text query.
    
    Uses semantic search with sentence transformers for natural language queries.
    Supports query expansion and hybrid search.
    """
    start_time = time.time()
    
    # Generate text embedding
    model = get_text_model()
    query_embedding = model.encode(request.query, normalize_embeddings=True).tolist()
    
    # Build filter conditions
    filter_conditions = build_filter_query(
        category=request.category,
        brand=request.brand,
        min_price=request.min_price,
        max_price=request.max_price,
        colors=request.colors,
        gender=request.gender
    )
    
    # Execute vector search
    conn = get_db_connection()
    try:
        products = execute_vector_search(
            conn=conn,
            query_embedding=query_embedding,
            embedding_column="text_embedding",
            limit=request.limit,
            filter_conditions=filter_conditions
        )
        
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            products=[ProductResponse(**dict(p)) for p in products],
            total=len(products),
            query_time_ms=round(query_time, 2)
        )
    finally:
        conn.close()

