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
from api.query_parser import QueryParser

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
    # Convert 0 to None for price filters (0 means "no filter")
    min_price_filter = None if (request.min_price is not None and request.min_price == 0) else request.min_price
    max_price_filter = None if (request.max_price is not None and request.max_price == 0) else request.max_price
    
    # Filter out "string" placeholder values from colors list
    colors_filter = None
    if request.colors:
        colors_filter = [c for c in request.colors if c.lower() != "string"]
        if not colors_filter:  # If all were "string", set to None
            colors_filter = None
    
    filter_conditions = build_filter_query(
        category=request.category,
        brand=request.brand,
        min_price=min_price_filter,
        max_price=max_price_filter,
        colors=colors_filter,
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
    text_query: Optional[str] = Form(None),
    limit: int = Form(20),
    category: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    min_price: Optional[float] = Form(None),
    max_price: Optional[float] = Form(None),
    colors: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    image_weight: float = Form(0.7, description="Weight for image embedding (0-1), text weight = 1 - image_weight")
):
    """
    Search products by uploaded image file with optional text query.
    
    Accepts an uploaded image file and optional text query (e.g., "same vibe but different colors").
    Combines image and text embeddings using CLIP for multimodal search.
    """
    start_time = time.time()
    
    # Validate weights
    if not 0 <= image_weight <= 1:
        raise HTTPException(status_code=400, detail="image_weight must be between 0 and 1")
    
    text_weight = 1.0 - image_weight
    
    # Read uploaded file
    contents = await image_file.read()
    try:
        image = Image.open(io.BytesIO(contents))
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Generate embeddings using CLIP (can encode both images and text)
    model, processor = get_clip_model()
    
    # Generate image embedding
    image_inputs = processor(images=image, return_tensors="pt")
    if torch.cuda.is_available():
        image_inputs = {k: v.cuda() for k, v in image_inputs.items()}
    
    with torch.no_grad():
        image_features = model.get_image_features(**image_inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        image_embedding_tensor = image_features[0]
    
    # Parse text query for filters, categories, and negative keywords
    query_parser = QueryParser()
    parsed_query = query_parser.parse(text_query) if text_query and text_query.strip() else {}
    
    # Override category from parsed query if found
    if parsed_query.get('categories') and not category:
        category = parsed_query['categories'][0]  # Use first category found
    
    # Merge price filters from query parsing
    min_price_from_query = parsed_query.get('min_price')
    max_price_from_query = parsed_query.get('max_price')
    if min_price_from_query is not None:
        min_price = min_price if min_price is not None else min_price_from_query
    if max_price_from_query is not None:
        max_price = max_price if max_price is not None else max_price_from_query
    
    # Generate text embedding if provided
    if text_query and text_query.strip():
        text_inputs = processor(text=[text_query.strip()], return_tensors="pt", padding=True, truncation=True)
        if torch.cuda.is_available():
            text_inputs = {k: v.cuda() for k, v in text_inputs.items()}
            # Ensure image embedding is on same device
            image_embedding_tensor = image_embedding_tensor.cuda()
        
        with torch.no_grad():
            text_features = model.get_text_features(**text_inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            text_embedding_tensor = text_features[0]
        
        # Combine embeddings with weighted average
        combined_embedding = (image_weight * image_embedding_tensor + text_weight * text_embedding_tensor)
        # Renormalize
        combined_embedding = combined_embedding / combined_embedding.norm(dim=-1, keepdim=True)
        query_embedding = combined_embedding.cpu().numpy().tolist()
    else:
        # Only image embedding
        query_embedding = image_embedding_tensor.cpu().numpy().tolist()
    
    # Parse colors filter
    color_list = None
    if colors:
        color_list = [c.strip() for c in colors.split(",") if c.strip()]
    
    # Build filter conditions with parsed query filters
    # Convert 0 to None for price filters (0 means "no filter")
    min_price_filter = None if (min_price is not None and min_price == 0) else min_price
    max_price_filter = None if (max_price is not None and max_price == 0) else max_price
    
    filter_conditions = build_filter_query(
        category=category,
        brand=brand,
        min_price=min_price_filter,
        max_price=max_price_filter,
        colors=color_list,
        gender=gender,
        exclude_categories=parsed_query.get('exclude_categories', []),
        exclude_keywords=parsed_query.get('exclude_keywords', []),
        keywords=parsed_query.get('keywords', [])
    )
    
    # Execute vector search with hybrid search if keywords found
    conn = get_db_connection()
    try:
        keywords_list = parsed_query.get('keywords', []) or []
        use_hybrid = bool(keywords_list) and len(keywords_list) > 0
        products = execute_vector_search(
            conn=conn,
            query_embedding=query_embedding,
            embedding_column="image_embedding",
            limit=limit,
            filter_conditions=filter_conditions,
            keywords=keywords_list if use_hybrid else None,
            use_hybrid=use_hybrid
        )
        
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            products=[ProductResponse(**dict(p)) for p in products],
            total=len(products),
            query_time_ms=round(query_time, 2)
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Print detailed error to console (visible in server terminal)
        print("=" * 80)
        print("ERROR in image upload search:")
        print(error_details)
        print("=" * 80)
        import logging
        logging.error(f"Image upload search error: {error_details}")
        # Provide more helpful error message
        error_msg = str(e)
        if "tuple index out of range" in error_msg:
            error_msg += " (SQL parameter mismatch)"
        raise HTTPException(status_code=500, detail=f"Search error: {error_msg}")
    finally:
        conn.close()


@router.post("/text", response_model=SearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Search products by text query.
    
    Uses semantic search with sentence transformers for natural language queries.
    Supports query expansion, hybrid search, negative filtering, and category extraction.
    """
    start_time = time.time()
    
    # Parse query for filters, categories, and negative keywords
    query_parser = QueryParser()
    parsed_query = query_parser.parse(request.query) if request.query else {}
    
    # Override category from parsed query if found
    category = request.category
    if parsed_query.get('categories') and not category:
        category = parsed_query['categories'][0]  # Use first category found
    
    # Merge price filters from query parsing
    min_price = request.min_price
    max_price = request.max_price
    min_price_from_query = parsed_query.get('min_price')
    max_price_from_query = parsed_query.get('max_price')
    if min_price_from_query is not None:
        min_price = min_price if min_price is not None else min_price_from_query
    if max_price_from_query is not None:
        max_price = max_price if max_price is not None else max_price_from_query
    
    # Generate text embedding
    model = get_text_model()
    query_embedding = model.encode(request.query, normalize_embeddings=True).tolist()
    
    # Build filter conditions
    # Convert 0 to None for price filters (0 means "no filter")
    min_price_filter = None if (min_price is not None and min_price == 0) else min_price
    max_price_filter = None if (max_price is not None and max_price == 0) else max_price
    
    # Filter out "string" placeholder values from colors list
    colors_filter = None
    if request.colors:
        colors_filter = [c for c in request.colors if c.lower() != "string"]
        if not colors_filter:  # If all were "string", set to None
            colors_filter = None
    
    filter_conditions = build_filter_query(
        category=category,
        brand=request.brand,
        min_price=min_price_filter,
        max_price=max_price_filter,
        colors=colors_filter,
        gender=request.gender,
        exclude_categories=parsed_query.get('exclude_categories', []),
        exclude_keywords=parsed_query.get('exclude_keywords', []),
        keywords=parsed_query.get('keywords', [])
    )
    
    # Debug: Log the filter conditions (remove in production)
    import logging
    logging.info(f"Text search filter: {filter_conditions}")
    logging.info(f"Parsed query: {parsed_query}")
    
    # Execute vector search with hybrid search if keywords found
    conn = get_db_connection()
    try:
        keywords_list = parsed_query.get('keywords', []) or []
        use_hybrid = bool(keywords_list) and len(keywords_list) > 0
        products = execute_vector_search(
            conn=conn,
            query_embedding=query_embedding,
            embedding_column="text_embedding",
            limit=request.limit,
            filter_conditions=filter_conditions,
            keywords=keywords_list if use_hybrid else None,
            use_hybrid=use_hybrid
        )
        
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            products=[ProductResponse(**dict(p)) for p in products],
            total=len(products),
            query_time_ms=round(query_time, 2)
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Print detailed error to console (visible in server terminal)
        print("=" * 80)
        print("ERROR in text search:")
        print(error_details)
        print("=" * 80)
        import logging
        logging.error(f"Text search error: {error_details}")
        # Provide more helpful error message
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=f"Search error: {error_msg}")
    finally:
        conn.close()

