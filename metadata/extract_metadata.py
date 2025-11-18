"""
Metadata extraction pipeline for products.
Extracts brands, colors, styles from product titles using NLP.
"""

import re
import os
from typing import List, Set, Optional
from collections import Counter

import psycopg2
from psycopg2.extras import execute_values


# Common color names (expanded list)
COLORS = {
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple',
    'pink', 'brown', 'gray', 'grey', 'beige', 'tan', 'navy', 'maroon',
    'burgundy', 'coral', 'teal', 'turquoise', 'lime', 'olive', 'khaki',
    'silver', 'gold', 'bronze', 'copper', 'ivory', 'cream', 'peach',
    'salmon', 'lavender', 'violet', 'indigo', 'cyan', 'magenta', 'amber',
    'rose', 'mint', 'sage', 'forest', 'emerald', 'ruby', 'sapphire',
    'charcoal', 'slate', 'stone', 'sand', 'camel', 'taupe', 'mauve',
    'plum', 'wine', 'burgundy', 'crimson', 'scarlet', 'vermillion',
    'aqua', 'azure', 'cerulean', 'cobalt', 'ultramarine', 'periwinkle',
    'mustard', 'ochre', 'saffron', 'tangerine', 'apricot', 'peach',
    'champagne', 'blush', 'rose gold', 'copper', 'bronze', 'brass',
    'gunmetal', 'matte black', 'gloss', 'matte', 'metallic'
}

# Style keywords
STYLES = {
    'minimal', 'minimalist', 'casual', 'formal', 'sporty', 'athletic',
    'street', 'streetwear', 'vintage', 'retro', 'modern', 'classic',
    'bohemian', 'boho', 'chic', 'elegant', 'edgy', 'grunge', 'punk',
    'preppy', 'prep', 'hipster', 'urban', 'rural', 'beach', 'summer',
    'winter', 'fall', 'autumn', 'spring', 'resort', 'cruise', 'holiday',
    'party', 'evening', 'daytime', 'work', 'office', 'business',
    'relaxed', 'comfortable', 'fitted', 'loose', 'oversized', 'slim',
    'skinny', 'wide', 'narrow', 'high', 'low', 'mid', 'ankle', 'knee',
    'thigh', 'crop', 'long', 'short', 'sleeveless', 'long sleeve',
    'short sleeve', 'tank', 'hoodie', 'sweatshirt', 'jacket', 'coat',
    'dress', 'skirt', 'pants', 'jeans', 'shorts', 'leggings', 'joggers'
}

# Brand extraction patterns (common brand name indicators)
BRAND_INDICATORS = ['by', 'from', 'brand']


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    if not text:
        return ""
    return text.lower().strip()


def extract_colors(title: str, description: str = "") -> List[str]:
    """
    Extract color names from product title and description.
    
    Args:
        title: Product title
        description: Product description (optional)
        
    Returns:
        List of extracted color names
    """
    text = normalize_text(f"{title} {description}")
    found_colors = []
    
    # Check for exact color matches
    for color in COLORS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(color) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_colors.append(color.title())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_colors = []
    for color in found_colors:
        if color.lower() not in seen:
            seen.add(color.lower())
            unique_colors.append(color)
    
    return unique_colors


def extract_styles(title: str, description: str = "") -> List[str]:
    """
    Extract style keywords from product title and description.
    
    Args:
        title: Product title
        description: Product description (optional)
        
    Returns:
        List of extracted style keywords
    """
    text = normalize_text(f"{title} {description}")
    found_styles = []
    
    for style in STYLES:
        pattern = r'\b' + re.escape(style) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_styles.append(style.title())
    
    # Remove duplicates
    seen = set()
    unique_styles = []
    for style in found_styles:
        if style.lower() not in seen:
            seen.add(style.lower())
            unique_styles.append(style)
    
    return unique_styles


def extract_brand_from_title(title: str, existing_brand: Optional[str] = None) -> List[str]:
    """
    Extract brand names from product title.
    If existing_brand is provided, prioritize it.
    
    Args:
        title: Product title
        existing_brand: Existing brand name from database
        
    Returns:
        List of extracted brand names
    """
    brands = []
    
    # If we already have a brand, use it
    if existing_brand and existing_brand.strip():
        brands.append(existing_brand.strip())
    
    # Try to extract brand from title (usually first word or two)
    # Common pattern: "Brand Name Product Title"
    words = title.split()
    if len(words) > 0:
        # First word is often the brand
        potential_brand = words[0]
        # Sometimes brand is two words
        if len(words) > 1:
            two_word_brand = f"{words[0]} {words[1]}"
            # Check if it looks like a brand (capitalized, not a common word)
            if two_word_brand[0].isupper() and len(two_word_brand) > 3:
                brands.append(two_word_brand)
        if potential_brand[0].isupper() and len(potential_brand) > 2:
            brands.append(potential_brand)
    
    # Remove duplicates
    seen = set()
    unique_brands = []
    for brand in brands:
        if brand.lower() not in seen:
            seen.add(brand.lower())
            unique_brands.append(brand)
    
    return unique_brands


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def extract_metadata_for_all_products(batch_size: int = 100):
    """
    Extract metadata for all products in the database.
    
    Args:
        batch_size: Number of products to process per batch
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all products
        cursor.execute("""
            SELECT id, product_id, title, description, brand_name
            FROM products
            ORDER BY id
        """)
        
        products = cursor.fetchall()
        print(f"Found {len(products)} products to process")
        
        updates = []
        processed = 0
        
        for product_id, db_product_id, title, description, brand_name in products:
            # Extract metadata
            colors = extract_colors(title, description or "")
            styles = extract_styles(title, description or "")
            brands = extract_brand_from_title(title, brand_name)
            
            # Prepare update
            updates.append({
                'id': product_id,
                'colors': colors,
                'styles': styles,
                'brands': brands
            })
            
            processed += 1
            
            # Process in batches
            if len(updates) >= batch_size:
                _update_metadata_batch(cursor, updates)
                conn.commit()
                print(f"Processed {processed}/{len(products)} products...")
                updates = []
        
        # Process remaining
        if updates:
            _update_metadata_batch(cursor, updates)
            conn.commit()
        
        print(f"\nSuccessfully processed {processed} products!")
        
        # Print statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN array_length(extracted_colors, 1) > 0 THEN 1 END) as with_colors,
                COUNT(CASE WHEN array_length(extracted_styles, 1) > 0 THEN 1 END) as with_styles,
                COUNT(CASE WHEN array_length(extracted_brands, 1) > 0 THEN 1 END) as with_brands
            FROM products
        """)
        stats = cursor.fetchone()
        print(f"\nMetadata Statistics:")
        print(f"  Total products: {stats[0]}")
        print(f"  With colors: {stats[1]}")
        print(f"  With styles: {stats[2]}")
        print(f"  With brands: {stats[3]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error extracting metadata: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _update_metadata_batch(cursor, updates: List[dict]):
    """Update metadata for a batch of products."""
    update_query = """
        UPDATE products
        SET 
            extracted_colors = %s,
            extracted_styles = %s,
            extracted_brands = %s
        WHERE id = %s
    """
    
    # Use regular execute for UPDATE queries (execute_values doesn't work with UPDATE)
    for update in updates:
        cursor.execute(update_query, (
            update['colors'],
            update['styles'],
            update['brands'],
            update['id']
        ))


def test_extraction():
    """Test metadata extraction with sample products."""
    test_cases = [
        ("Hellstar Thorn T-Shirt Green", "Hellstar", ""),
        ("Stanley Quencher H2.0 Flowstate Tumbler Pink Mesa Sunset", "Stanley", ""),
        ("Nike Air Max 90 Black White", "Nike", "Classic sneaker in black and white"),
        ("Adidas Originals Superstar White", "Adidas", "Classic white sneakers"),
    ]
    
    print("Testing metadata extraction:")
    print("=" * 60)
    
    for title, brand, desc in test_cases:
        colors = extract_colors(title, desc)
        styles = extract_styles(title, desc)
        brands = extract_brand_from_title(title, brand)
        
        print(f"\nTitle: {title}")
        print(f"  Colors: {colors}")
        print(f"  Styles: {styles}")
        print(f"  Brands: {brands}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_extraction()
    else:
        print("Starting metadata extraction...")
        print("-" * 50)
        extract_metadata_for_all_products()
        print("\nMetadata extraction completed!")

