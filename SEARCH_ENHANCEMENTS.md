# Search Enhancements - Query Parsing & Hybrid Search

## Overview
Enhanced the search system to handle natural language queries with:
1. **Query Parsing** - Extracts categories, negative keywords, and price filters from text
2. **Negative Filtering** - Excludes unwanted categories/keywords
3. **Category Extraction** - Automatically filters by category from text queries
4. **Price Detection** - Extracts price filters from natural language
5. **Hybrid Search** - Combines vector similarity with keyword matching

## Features Implemented

### 1. Visual Question Answering ✅
**Query:** "Show me shoes that would match this outfit"

**How it works:**
- Parses query to extract "shoes" category
- Filters results to only show footwear
- Uses hybrid search (vector + keyword matching) to boost relevance

**Implementation:**
- `QueryParser` extracts category keywords from query
- `build_filter_query` applies category filter
- `execute_vector_search` uses hybrid scoring when keywords found

### 2. Style Transfer Search ✅
**Query:** "Find items with the same vibe but in different colors"

**How it works:**
- CLIP embeddings capture visual "vibe"
- Text query modifies the embedding space
- Color filters can be applied separately

**Status:** Already working (uses CLIP multimodal capabilities)

### 3. Negative Search ✅
**Query:** "Similar to this but NOT sneakers"

**How it works:**
- Parses "NOT sneakers" to extract exclude keyword
- Maps "sneakers" to "shoes" category
- Excludes products with "sneakers" in title/category/sub_category

**Implementation:**
- `QueryParser` detects negative patterns: `not`, `no`, `exclude`, `except`, `without`, `avoid`
- `build_filter_query` adds exclusion conditions:
  ```sql
  LOWER(title) NOT LIKE '%sneakers%'
  AND LOWER(category) NOT LIKE '%sneakers%'
  AND LOWER(sub_category) NOT LIKE '%sneakers%'
  ```

### 4. Budget Alternatives ✅
**Query:** "Show me similar items under $50"

**How it works:**
- Extracts price from query: "under $50" → `max_price = 50`
- Applies price filter: `lowest_price <= 50`

**Implementation:**
- `QueryParser` detects price patterns:
  - `under $50`, `below $50`, `less than $50`
  - `over $50`, `above $50`, `more than $50`
  - `$50-$100` (ranges)
- Price filters applied in SQL: `lowest_price <= 50`

**Note:** Currently works with "under 50 dollars" format. "$50" format needs pattern refinement.

### 5. Complete the Look
**Query:** "Show me matching tops for these shoes"

**How it works:**
- Extracts "tops" category from query
- Filters to only show tops/shirts/hoodies
- Uses vector similarity to find matching styles

**Implementation:**
- Category mapping includes: `tops`, `bottoms`, `shoes`, `accessories`, `dresses`, `outerwear`
- Automatically filters by extracted category

## Technical Implementation

### Files Created/Modified

1. **`api/query_parser.py`** (NEW)
   - `QueryParser` class for parsing natural language queries
   - Extracts: categories, exclude_categories, exclude_keywords, min_price, max_price, keywords
   - Category keyword mappings
   - Negative pattern detection
   - Price pattern detection

2. **`api/search_utils.py`** (MODIFIED)
   - Added `exclude_categories`, `exclude_keywords`, `keywords` parameters to `build_filter_query`
   - Added negative filtering SQL conditions
   - Added hybrid search scoring in `execute_vector_search`
   - Keyword boosting: +0.3 for title match, +0.2 for category, +0.1 for sub_category

3. **`api/routers/search.py`** (MODIFIED)
   - Integrated `QueryParser` into image upload and text search endpoints
   - Parses text queries before generating embeddings
   - Merges parsed filters with explicit filters
   - Enables hybrid search when keywords detected

## Category Mappings

```python
CATEGORY_KEYWORDS = {
    'shoes': ['shoes', 'shoe', 'footwear', 'sneakers', 'sneaker', 'boots', ...],
    'tops': ['shirt', 'shirts', 'top', 'tops', 't-shirt', 'tshirt', 'hoodie', ...],
    'bottoms': ['pants', 'trousers', 'jeans', 'shorts', 'skirt', ...],
    'accessories': ['bag', 'handbag', 'watch', 'sunglasses', 'belt', ...],
    'dresses': ['dress', 'dresses', 'gown', ...],
    'outerwear': ['jacket', 'coat', 'blazer', 'parka', ...],
}
```

## Usage Examples

### Image + Text Search
```python
POST /api/search/image/upload
- image_file: <uploaded image>
- text_query: "Show me shoes that would match this outfit"
- Result: Only footwear products, filtered by category
```

### Negative Search
```python
POST /api/search/image/upload
- image_file: <uploaded image>
- text_query: "Similar to this but NOT sneakers"
- Result: Similar items excluding sneakers
```

### Budget Search
```python
POST /api/search/text
- query: "Show me similar items under $50"
- Result: Products with price <= 50
```

## Limitations & Future Improvements

1. **Price Parsing**: "$50" format needs better pattern matching
   - Current: Works with "under 50 dollars"
   - TODO: Improve regex to handle "$50" directly

2. **BM25 Search**: Not yet implemented
   - Current: Keyword matching via LIKE queries
   - Future: Add PostgreSQL full-text search (tsvector) for better keyword matching
   - Benefit: Better ranking, phrase matching, stemming

3. **Category Mapping**: Could be expanded
   - Add more fashion categories
   - Support synonyms (e.g., "sneakers" = "athletic shoes")
   - Use LLM for better category extraction

4. **Hybrid Search**: Could be improved
   - Current: Simple keyword boosting
   - Future: Weighted combination of vector + BM25 scores
   - Benefit: Better relevance ranking

## Testing

Test the parser:
```python
from api.query_parser import QueryParser

qp = QueryParser()
result = qp.parse("Show me shoes that would match this outfit")
# Returns: {'categories': ['shoes'], 'keywords': ['shoe', 'shoes'], ...}
```

## Next Steps

1. ✅ Query parsing implemented
2. ✅ Negative filtering implemented
3. ✅ Category extraction implemented
4. ✅ Price detection implemented (partial)
5. ⏳ Improve "$50" price pattern matching
6. ⏳ Add BM25 full-text search for better keyword matching
7. ⏳ Expand category mappings
8. ⏳ Add LLM-based query understanding for complex queries

