"""
Search utility functions for vector similarity search.
"""

from typing import List, Optional, Dict, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor


def build_filter_query(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    colors: Optional[List[str]] = None,
    gender: Optional[str] = None,
    exclude_categories: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None
) -> Tuple[str, List]:
    """
    Build SQL WHERE clause for filtering products using parameterized queries.
    
    Args:
        category: Filter by category
        brand: Filter by brand name
        min_price: Minimum price
        max_price: Maximum price
        colors: List of colors to filter by
        gender: Filter by gender
        exclude_categories: Categories to exclude
        exclude_keywords: Keywords to exclude (LIKE patterns)
        keywords: Keywords to include (for reference, used in hybrid search)
        
    Returns:
        Tuple of (SQL WHERE clause string, list of parameters for LIKE patterns)
        Example: ("category = %s AND is_active = TRUE", ["shoes"])
    """
    conditions = []
    params = []
    
    # Ignore placeholder "string" values from API docs
    if category and category.lower() != "string":
        conditions.append("category = %s")
        params.append(category)
    
    if brand and brand.lower() != "string":
        conditions.append("brand_name = %s")
        params.append(brand)
    
    if min_price is not None and min_price > 0:
        conditions.append("lowest_price >= %s")
        params.append(min_price)
    
    if max_price is not None and max_price > 0:
        conditions.append("lowest_price <= %s")
        params.append(max_price)
    
    if colors:
        # Check if any of the colors match in extracted_colors array
        # Ignore placeholder "string" values from API docs
        color_conditions = []
        for color in colors:
            if color.lower() != "string":
                color_conditions.append("%s = ANY(extracted_colors)")
                params.append(color)
        if color_conditions:
            conditions.append(f"({' OR '.join(color_conditions)})")
    
    # Ignore placeholder "string" values from API docs
    if gender and gender.lower() != "string":
        conditions.append("gender = %s")
        params.append(gender)
    
    # Exclude categories (negative filtering) - use parameterized LIKE
    if exclude_categories and len(exclude_categories) > 0:
        exclude_conditions = []
        for cat in exclude_categories:
            if cat and cat.lower() != "string":
                # Use parameterized queries for all LIKE patterns
                exclude_conditions.append(
                    "(category != %s AND sub_category != %s AND LOWER(title) NOT LIKE %s)"
                )
                params.extend([cat, cat, f"%{cat.lower()}%"])
        if exclude_conditions:
            # All exclusions must be satisfied (AND)
            conditions.append(f"({' AND '.join(exclude_conditions)})")
    
    # Exclude keywords (negative filtering) - use parameterized LIKE
    if exclude_keywords and len(exclude_keywords) > 0:
        exclude_keyword_conditions = []
        for keyword in exclude_keywords:
            if keyword and keyword.lower() != "string":
                # Use parameterized LIKE patterns - no % in SQL string!
                exclude_keyword_conditions.append(
                    "(LOWER(title) NOT LIKE %s AND LOWER(category) NOT LIKE %s AND LOWER(sub_category) NOT LIKE %s)"
                )
                keyword_pattern = f"%{keyword.lower()}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        if exclude_keyword_conditions:
            # All keyword exclusions must be satisfied (AND)
            conditions.append(f"({' AND '.join(exclude_keyword_conditions)})")
    
    # Keyword matching (positive filtering) - not used in WHERE clause, only in hybrid search scoring
    # We don't add these to conditions, they're handled in execute_vector_search for boosting
    
    # Only return active products with embeddings
    conditions.append("is_active = TRUE")
    
    if conditions:
        return (" AND ".join(conditions), params)
    return ("is_active = TRUE", [])


def execute_vector_search(
    conn: psycopg2.extensions.connection,
    query_embedding: List[float],
    embedding_column: str,
    limit: int = 20,
    filter_conditions: Tuple[str, List] = ("", []),
    keywords: Optional[List[str]] = None,
    use_hybrid: bool = False
) -> List[Dict]:
    """
    Execute vector similarity search using pgvector with parameterized queries.
    
    Args:
        conn: Database connection
        query_embedding: Query embedding vector
        embedding_column: Name of the embedding column ('image_embedding' or 'text_embedding')
        limit: Maximum number of results
        filter_conditions: Tuple of (SQL WHERE clause string, list of parameters)
        keywords: Keywords for hybrid search boosting
        use_hybrid: Whether to use hybrid search with keyword boosting
        
    Returns:
        List of product dictionaries with similarity scores
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Convert embedding list to PostgreSQL vector format: '[0.1, 0.2, ...]'
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Unpack filter conditions and params
        filter_sql, filter_params = filter_conditions if isinstance(filter_conditions, tuple) else (filter_conditions, [])
        
        # Build the query with optional keyword boosting
        # Use cosine distance (1 - cosine similarity) for pgvector
        # <=> operator returns cosine distance (0 = identical, 2 = opposite)
        
        # Calculate keyword match score if keywords provided (for hybrid search)
        keyword_score = ""
        keyword_score_params = []
        # Ensure keywords is a list and not empty, and use_hybrid is True
        if keywords is not None and isinstance(keywords, list) and len(keywords) > 0 and use_hybrid:
            keyword_conditions = []
            for keyword in keywords:
                if keyword.lower() != "string":
                    keyword_pattern = f"%{keyword.lower()}%"
                    # Use parameterized LIKE patterns - no % in SQL string!
                    keyword_conditions.append("""
                        CASE 
                            WHEN LOWER(title) LIKE %s THEN 0.3
                            WHEN LOWER(category) LIKE %s THEN 0.2
                            WHEN LOWER(sub_category) LIKE %s THEN 0.1
                            ELSE 0
                        END
                    """)
                    keyword_score_params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            if keyword_conditions:
                keyword_score = f" + ({' + '.join(keyword_conditions)})"
        
        # Build query based on whether we have keyword scoring
        if keyword_score and keyword_score.strip():
            # Hybrid search: use computed similarity_score
            query = f"""
                SELECT 
                    id,
                    product_id,
                    title,
                    category,
                    sub_category,
                    brand_name,
                    featured_image,
                    lowest_price,
                    pdp_url,
                    (1 - ({embedding_column} <=> %s::vector)){keyword_score} as similarity_score
                FROM products
                WHERE {embedding_column} IS NOT NULL
                AND {filter_sql}
                ORDER BY similarity_score DESC
                LIMIT %s
            """
            # Combine all parameters: embedding, keyword_score params, filter params, limit
            all_params = [embedding_str] + keyword_score_params + filter_params + [limit]
            cursor.execute(query, all_params)
        else:
            # Pure vector search: order by distance directly
            query = f"""
                SELECT 
                    id,
                    product_id,
                    title,
                    category,
                    sub_category,
                    brand_name,
                    featured_image,
                    lowest_price,
                    pdp_url,
                    1 - ({embedding_column} <=> %s::vector) as similarity_score
                FROM products
                WHERE {embedding_column} IS NOT NULL
                AND {filter_sql}
                ORDER BY {embedding_column} <=> %s::vector
                LIMIT %s
            """
            # Combine all parameters: embedding (twice), filter params, limit
            all_params = [embedding_str, embedding_str] + filter_params + [limit]
            cursor.execute(query, all_params)
        
        results = cursor.fetchall()
        return results
        
    finally:
        cursor.close()

