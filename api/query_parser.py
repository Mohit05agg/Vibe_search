"""
Query parser for extracting filters, categories, and negative keywords from natural language queries.
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Category mappings
CATEGORY_KEYWORDS = {
    'shoes': ['shoes', 'shoe', 'footwear', 'sneakers', 'sneaker', 'boots', 'boot', 'sandals', 'sandal', 'heels', 'heel', 'flats', 'flat'],
    'tops': ['shirt', 'shirts', 'top', 'tops', 't-shirt', 'tshirt', 'blouse', 'blouses', 'sweater', 'sweaters', 'hoodie', 'hoodies', 'jacket', 'jackets', 'coat', 'coats'],
    'bottoms': ['pants', 'pant', 'trousers', 'trouser', 'jeans', 'jean', 'shorts', 'short', 'skirt', 'skirts'],
    'accessories': ['accessory', 'accessories', 'bag', 'bags', 'handbag', 'handbags', 'watch', 'watches', 'sunglasses', 'belt', 'belts', 'jewelry', 'jewellery'],
    'dresses': ['dress', 'dresses', 'gown', 'gowns'],
    'outerwear': ['jacket', 'jackets', 'coat', 'coats', 'blazer', 'blazers', 'parka', 'parkas'],
}

# Negative keyword patterns
NEGATIVE_PATTERNS = [
    r'\bnot\s+(\w+)',
    r'\bno\s+(\w+)',
    r'\bexclude\s+(\w+)',
    r'\bexcept\s+(\w+)',
    r'\bwithout\s+(\w+)',
    r'\bavoid\s+(\w+)',
]

# Price patterns
PRICE_PATTERNS = [
    r'\bunder\s+\$?(\d+)',
    r'\bbelow\s+\$?(\d+)',
    r'\bless\s+than\s+\$?(\d+)',
    r'\bmax\s+\$?(\d+)',
    r'\bmaximum\s+\$?(\d+)',
    r'\bover\s+\$?(\d+)',
    r'\babove\s+\$?(\d+)',
    r'\bmore\s+than\s+\$?(\d+)',
    r'\bmin\s+\$?(\d+)',
    r'\bminimum\s+\$?(\d+)',
    r'\b\$?(\d+)\s*-\s*\$?(\d+)',  # Range: $50-$100
    r'\$(\d+)',  # Simple $50 format
    r'\b(\d+)\s*dollars?\b',  # 50 dollars
]


class QueryParser:
    """Parse natural language queries to extract filters and categories."""
    
    def __init__(self):
        self.category_keywords = self._build_category_keywords()
    
    def _build_category_keywords(self) -> Dict[str, List[str]]:
        """Build reverse mapping from keywords to categories."""
        keyword_to_category = defaultdict(list)
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                keyword_to_category[keyword.lower()].append(category)
        return dict(keyword_to_category)
    
    def parse(self, query: str) -> Dict:
        """
        Parse a natural language query and extract:
        - Categories to include
        - Categories to exclude (negative)
        - Price filters
        - Other keywords
        
        Returns:
            {
                'categories': ['shoes'],
                'exclude_categories': ['sneakers'],
                'exclude_keywords': ['sneakers'],
                'min_price': None,
                'max_price': 50.0,
                'keywords': ['shoes', 'match', 'outfit']
            }
        """
        if not query:
            return {
                'categories': [],
                'exclude_categories': [],
                'exclude_keywords': [],
                'min_price': None,
                'max_price': None,
                'keywords': []
            }
        
        query_lower = query.lower()
        result = {
            'categories': [],
            'exclude_categories': [],
            'exclude_keywords': [],
            'min_price': None,
            'max_price': None,
            'keywords': []
        }
        
        # Extract negative keywords
        exclude_keywords = []
        for pattern in NEGATIVE_PATTERNS:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                keyword = match.group(1).strip()
                # Skip if it's a stop word or price
                if keyword and keyword not in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
                    exclude_keywords.append(keyword)
                    # Don't auto-exclude categories for specific items (e.g., "sneaker" shouldn't exclude all "shoes")
                    # Only exclude category if it's a direct category name match, not a subcategory
                    # For now, we'll rely on keyword exclusion which is more precise
                    pass
        
        result['exclude_keywords'] = list(set(exclude_keywords))
        
        # Extract price filters - check context around price mentions
        # First, find all price mentions with context
        price_context_pattern = r'(under|below|less than|max|maximum|over|above|more than|min|minimum)?\s*\$?(\d+)\s*(dollars?)?'
        price_matches = list(re.finditer(price_context_pattern, query_lower, re.IGNORECASE))
        
        for match in price_matches:
            try:
                context = match.group(1) or ""
                value = float(match.group(2))
                context_lower = context.lower() if context else ""
                
                # Check context in the match itself
                if 'under' in context_lower or 'below' in context_lower or 'less' in context_lower or 'max' in context_lower:
                    if result['max_price'] is None or value < result['max_price']:
                        result['max_price'] = value
                elif 'over' in context_lower or 'above' in context_lower or 'more' in context_lower or 'min' in context_lower:
                    if result['min_price'] is None or value > result['min_price']:
                        result['min_price'] = value
                # Check if there's "under" or "below" before this match in the query
                elif match.start() > 0:
                    # Look back 30 characters for context
                    start_pos = max(0, match.start() - 30)
                    context_before = query_lower[start_pos:match.start()]
                    if 'under' in context_before or 'below' in context_before or 'less' in context_before:
                        if result['max_price'] is None or value < result['max_price']:
                            result['max_price'] = value
                    elif 'over' in context_before or 'above' in context_before or 'more' in context_before:
                        if result['min_price'] is None or value > result['min_price']:
                            result['min_price'] = value
            except (ValueError, IndexError, AttributeError):
                continue
        
        # Also check range patterns
        range_pattern = r'\$?(\d+)\s*-\s*\$?(\d+)'
        range_matches = re.finditer(range_pattern, query_lower)
        for match in range_matches:
            try:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                result['min_price'] = min_val
                result['max_price'] = max_val
            except (ValueError, IndexError):
                continue
        
        # Extract category keywords (positive)
        found_categories = set()
        for keyword, categories in self.category_keywords.items():
            if keyword in query_lower:
                found_categories.update(categories)
                # Also add the keyword itself for keyword matching
                result['keywords'].append(keyword)
        
        result['categories'] = list(found_categories)
        
        # Extract other important keywords (non-category)
        # Don't include excluded keywords in the keywords list
        words = re.findall(r'\b\w+\b', query_lower)
        exclude_keywords_lower = [k.lower() for k in exclude_keywords]
        for word in words:
            if word not in ['show', 'me', 'find', 'search', 'that', 'would', 'match', 'this', 'outfit', 'items', 'similar', 'to', 'but', 'not', 'no', 'with', 'the', 'a', 'an', 'outfit']:
                if word not in self.category_keywords and word not in exclude_keywords_lower:
                    result['keywords'].append(word)
        
        # Remove excluded keywords from keywords list
        result['keywords'] = [k for k in result['keywords'] if k.lower() not in exclude_keywords_lower]
        result['keywords'] = list(set(result['keywords']))
        result['exclude_categories'] = list(set(result['exclude_categories']))
        
        return result


def parse_query_for_filters(query: str) -> Tuple[Optional[str], List[str], Optional[float], Optional[float]]:
    """
    Parse query and return (category, exclude_keywords, min_price, max_price).
    Simplified version for backward compatibility.
    """
    parser = QueryParser()
    parsed = parser.parse(query)
    
    # Get primary category (first one found)
    category = parsed['categories'][0] if parsed['categories'] else None
    
    # Get exclude keywords
    exclude_keywords = parsed['exclude_keywords']
    
    return category, exclude_keywords, parsed['min_price'], parsed['max_price']

