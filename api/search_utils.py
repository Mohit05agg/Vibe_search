"""
Search utility functions for vector similarity search.
"""

from typing import List, Optional, Dict
import psycopg2
from psycopg2.extras import RealDictCursor


def build_filter_query(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    colors: Optional[List[str]] = None,
    gender: Optional[str] = None
) -> str:
    """
    Build SQL WHERE clause for filtering products.
    
    Args:
        category: Filter by category
        brand: Filter by brand name
        min_price: Minimum price
        max_price: Maximum price
        colors: List of colors to filter by
        gender: Filter by gender
        
    Returns:
        SQL WHERE clause string
    """
    conditions = []
    
    # Ignore placeholder "string" values from API docs
    if category and category.lower() != "string":
        category_escaped = category.replace("'", "''")
        conditions.append(f"category = '{category_escaped}'")
    
    if brand and brand.lower() != "string":
        brand_escaped = brand.replace("'", "''")
        conditions.append(f"brand_name = '{brand_escaped}'")
    
    if min_price is not None and min_price > 0:
        conditions.append(f"lowest_price >= {min_price}")
    
    if max_price is not None and max_price > 0:
        conditions.append(f"lowest_price <= {max_price}")
    
    if colors:
        # Check if any of the colors match in extracted_colors array
        # Ignore placeholder "string" values from API docs
        color_conditions = []
        for color in colors:
            if color.lower() != "string":
                color_clean = color.replace("'", "''")
                color_conditions.append(f"'{color_clean}' = ANY(extracted_colors)")
        if color_conditions:
            conditions.append(f"({' OR '.join(color_conditions)})")
    
    # Ignore placeholder "string" values from API docs
    if gender and gender.lower() != "string":
        gender_escaped = gender.replace("'", "''")
        conditions.append(f"gender = '{gender_escaped}'")
    
    # Only return active products with embeddings
    conditions.append("is_active = TRUE")
    
    if conditions:
        return " AND ".join(conditions)
    return "is_active = TRUE"


def execute_vector_search(
    conn: psycopg2.extensions.connection,
    query_embedding: List[float],
    embedding_column: str,
    limit: int = 20,
    filter_conditions: str = ""
) -> List[Dict]:
    """
    Execute vector similarity search using pgvector.
    
    Args:
        conn: Database connection
        query_embedding: Query embedding vector
        embedding_column: Name of the embedding column ('image_embedding' or 'text_embedding')
        limit: Maximum number of results
        filter_conditions: SQL WHERE clause for filtering
        
    Returns:
        List of product dictionaries with similarity scores
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Convert embedding list to PostgreSQL vector format: '[0.1, 0.2, ...]'
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Build the query
        # Use cosine distance (1 - cosine similarity) for pgvector
        # <=> operator returns cosine distance (0 = identical, 2 = opposite)
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
            AND {filter_conditions}
            ORDER BY {embedding_column} <=> %s::vector
            LIMIT %s
        """
        
        # Execute with query embedding (used twice: once in SELECT, once in ORDER BY)
        cursor.execute(query, (embedding_str, embedding_str, limit))
        
        results = cursor.fetchall()
        return results
        
    finally:
        cursor.close()

