# File-by-File Explanation Guide

Complete explanation of every file in the project, organized by component.

## 📊 Database Layer

### `database/schema.sql`
**Purpose:** Defines the database structure

**Key Sections:**
```sql
-- Products table: Stores all product information
CREATE TABLE products (
    id, product_id, title, category, brand_name,
    featured_image, lowest_price,
    extracted_colors[], extracted_styles[], extracted_brands[],
    image_embedding vector(512),  -- CLIP embeddings
    text_embedding vector(384)    -- Text embeddings
)

-- Scraped images table: Stores Pinterest/Instagram images
CREATE TABLE scraped_images (
    source, image_url, caption, hashtags[],
    engagement_count, image_embedding vector(512)
)
```

**Why it matters:**
- Foundation of the entire system
- Vector columns enable similarity search
- Indexes make searches fast

### `database/import_products.py`
**Purpose:** Imports CSV data into database

**Key Functions:**
- `parse_bool()` - Converts string booleans
- `parse_decimal()` - Converts prices
- `import_products_from_csv()` - Main import function

**What to understand:**
- How CSV columns map to database
- Data type conversions
- Batch insertion for efficiency

### `database/setup_database.py`
**Purpose:** Creates database schema

**What it does:**
- Executes `schema.sql`
- Creates all tables
- Sets up indexes

## 🤖 AI/ML Layer

### `embeddings/generate_clip_embeddings.py`
**Purpose:** Generates image embeddings using CLIP

**Key Functions:**
- `download_image()` - Gets image from URL
- `generate_clip_embedding()` - Creates 512-dim vector
- `process_products_batch()` - Processes multiple products

**Flow:**
```
Product Image URL → Download → CLIP Model → Vector → Database
```

**Key Concepts:**
- CLIP model understands images semantically
- Embeddings are normalized for comparison
- Batch processing for efficiency

### `embeddings/generate_text_embeddings.py`
**Purpose:** Generates text embeddings

**Key Functions:**
- `generate_text_embedding()` - Creates 384-dim vector
- Uses sentence-transformers model

**Flow:**
```
Product Title → Sentence Transformer → Vector → Database
```

**Key Concepts:**
- Semantic understanding (not just keywords)
- "beach shorts" matches "swim trunks"
- Normalized for cosine similarity

### `embeddings/check_embedding_status.py`
**Purpose:** Checks embedding generation progress

**What it shows:**
- Total products
- Products with image embeddings
- Products with text embeddings
- Coverage statistics

## 🔍 Metadata Layer

### `metadata/extract_metadata.py`
**Purpose:** Extracts colors, styles, brands from product titles

**Key Functions:**
- `extract_colors()` - Finds color names
- `extract_styles()` - Finds style keywords
- `extract_brand_from_title()` - Gets brand

**How it works:**
- Uses keyword lists (COLORS, STYLES)
- Regex pattern matching
- Stores in database arrays

**Example:**
```
"Black Nike Sneakers" → 
  Colors: ["Black"]
  Styles: []
  Brands: ["Nike", "Black Nike"]
```

## 🌐 Backend API

### `api/main.py`
**Purpose:** FastAPI application entry point

**Key Components:**
- FastAPI app creation
- CORS configuration
- Router registration
- Root endpoint

**Structure:**
```python
app = FastAPI(...)
app.add_middleware(CORSMiddleware, ...)
app.include_router(health.router)
app.include_router(search.router)
app.include_router(feed.router)
```

### `api/models.py`
**Purpose:** Defines API request/response structures

**Key Models:**
- `ProductResponse` - Product data structure
- `SearchResponse` - Search results format
- `ImageSearchRequest` - Image search parameters
- `TextSearchRequest` - Text search parameters

**Why it matters:**
- Type safety
- Automatic validation
- API documentation

### `api/database.py`
**Purpose:** Database connection management

**Key Function:**
- `get_db_connection()` - Creates PostgreSQL connection

**Configuration:**
- Uses environment variables
- Defaults to localhost
- Handles connection errors

### `api/search_utils.py`
**Purpose:** Core search functionality

**Key Functions:**
- `build_filter_query()` - Creates SQL WHERE clause
- `execute_vector_search()` - Runs vector similarity search

**Vector Search:**
```sql
SELECT *, 1 - (embedding <=> query_vector) as similarity
FROM products
WHERE embedding IS NOT NULL
ORDER BY embedding <=> query_vector
LIMIT 20
```

**Key Concepts:**
- `<=>` operator: Cosine distance
- `1 - distance` = similarity score
- HNSW index for fast search

### `api/routers/health.py`
**Purpose:** Health check endpoint

**Endpoint:** `GET /api/health`

**What it does:**
- Tests database connection
- Returns status

### `api/routers/search.py`
**Purpose:** Search endpoints

**Endpoints:**
- `POST /api/search/text` - Text search
- `POST /api/search/image` - Image search by URL
- `POST /api/search/image/upload` - Image search by upload

**Key Functions:**
- `search_by_text()` - Handles text queries
- `search_by_image()` - Handles image URLs
- `search_by_image_upload()` - Handles file uploads
- `get_clip_model()` - Lazy loads CLIP
- `get_text_model()` - Lazy loads sentence transformer

**Flow (Text Search):**
```
Request → Generate text embedding → Vector search → Filter → Return results
```

**Flow (Image Search):**
```
Request → Download/Process image → CLIP embedding → Vector search → Return results
```

### `api/routers/feed.py`
**Purpose:** Scraped images feed

**Endpoint:** `GET /api/scraped-images`

**What it does:**
- Returns scraped images for explore feed
- Supports pagination

## 🎨 Frontend

### `frontend/app/layout.tsx`
**Purpose:** Root layout component

**What it does:**
- Wraps all pages
- Sets metadata
- Includes global CSS

### `frontend/app/page.tsx`
**Purpose:** Main application page

**Key State:**
- `searchResults` - Current search results
- `selectedProduct` - Product in modal
- `activeTab` - Current tab (search/explore)

**Key Functions:**
- `handleSearchResults()` - Updates results
- `handleImageClick()` - Click-to-search from feed

**Component Structure:**
```
Home
├── SearchInterface
├── ExploreFeed (if activeTab === "explore")
├── ResultsGrid (if activeTab === "search")
└── ProductModal (if selectedProduct)
```

### `frontend/components/SearchInterface.tsx`
**Purpose:** Search input interface

**Features:**
- Text search input
- Image file upload
- Tab switching (text/image)
- Loading states

**Key Functions:**
- `handleTextSearch()` - Sends text query to API
- `handleImageUpload()` - Uploads image for search
- `handleFileChange()` - Handles file selection

**API Calls:**
```typescript
// Text search
POST /api/search/text
Body: { query: "black sneakers", limit: 20 }

// Image search
POST /api/search/image/upload
FormData: { image_file: File, limit: 20 }
```

### `frontend/components/ResultsGrid.tsx`
**Purpose:** Displays search results

**Features:**
- Grid layout
- Product cards with images
- Similarity scores
- Click to view details

**Structure:**
```
ResultsGrid
└── Product Cards
    ├── Image
    ├── Title
    ├── Brand
    ├── Price
    └── Similarity Score
```

### `frontend/components/ExploreFeed.tsx`
**Purpose:** Shows scraped fashion images

**Features:**
- Grid of scraped images
- Click-to-search functionality
- Fetches from `/api/scraped-images`

**Flow:**
```
Load → Fetch images from API → Display grid → User clicks → Trigger image search
```

### `frontend/components/ProductModal.tsx`
**Purpose:** Product detail modal

**Features:**
- Shows full product information
- Large product image
- All attributes
- Link to product page

### `frontend/types/index.ts`
**Purpose:** TypeScript type definitions

**Key Types:**
- `Product` - Product structure
- `SearchResponse` - API response
- `ScrapedImage` - Scraped image structure

## 🕷️ Scrapers

### `scrapers/base_scraper.py`
**Purpose:** Base class for all scrapers

**Features:**
- Rate limiting
- User agent rotation
- Retry logic
- Database saving

**Key Methods:**
- `get_random_user_agent()` - Rotates user agents
- `random_delay()` - Adds delays
- `save_scraped_image()` - Saves to database

### `scrapers/pinterest_scraper.py`
**Purpose:** Scrapes Pinterest boards

**Key Functions:**
- `scrape_board()` - Main scraping function
- `extract_hashtags()` - Gets hashtags from text
- `_parse_engagement()` - Parses like counts

**Flow:**
```
Open browser → Navigate to board → Scroll → Extract pins → Save to DB
```

**Technologies:**
- Playwright for browser automation
- BeautifulSoup for parsing

### `scrapers/instagram_scraper.py`
**Purpose:** Scrapes Instagram profiles

**Note:** Limited by Instagram's anti-bot measures

**Similar to Pinterest scraper but:**
- Longer delays (3-7 seconds)
- More error handling
- May require login for some profiles

### `scrapers/run_scrapers.py`
**Purpose:** Main scraper script

**Features:**
- Command-line interface
- Supports multiple targets
- Configurable limits

**Usage:**
```bash
python scrapers/run_scrapers.py --source pinterest --limit 50
```

## 🧪 Testing

### `tests/test_database.py`
**Purpose:** Database tests

**Tests:**
- Connection
- pgvector extension
- Tables exist
- Products have embeddings
- Vector search works

### `tests/test_api.py`
**Purpose:** API endpoint tests

**Tests:**
- Health endpoint
- Text search
- Image search
- Response times
- Error handling

### `test_full_project.py`
**Purpose:** Complete project test

**Tests everything:**
- Backend health
- Frontend accessibility
- Database connection
- All API endpoints
- Search functionality
- Performance

## 🚀 Startup Scripts

### `run_server.py`
**Purpose:** Starts FastAPI backend

**What it does:**
- Runs uvicorn server
- Enables auto-reload
- Listens on port 8000

### `start_all.ps1`
**Purpose:** Starts both servers

**What it does:**
- Opens backend in new window
- Opens frontend in new window
- Shows status

## 📝 Configuration Files

### `requirements.txt`
**Purpose:** Python dependencies

**Key Packages:**
- `fastapi` - Web framework
- `psycopg2-binary` - PostgreSQL driver
- `torch`, `transformers` - AI models
- `sentence-transformers` - Text embeddings
- `playwright` - Browser automation

### `frontend/package.json`
**Purpose:** Node.js dependencies

**Key Packages:**
- `next` - React framework
- `react`, `react-dom` - UI library
- `tailwindcss` - Styling

### `.gitignore`
**Purpose:** Files to exclude from Git

**Excludes:**
- `.venv/` - Virtual environment
- `node_modules/` - Node dependencies
- `__pycache__/` - Python cache
- `.env` - Environment variables

## 🔄 Complete Request Flow Example

### Text Search Request:

1. **User Action:** Types "black sneakers" in frontend
2. **Frontend:** `SearchInterface.tsx` → `handleTextSearch()`
3. **API Call:** `POST http://localhost:8000/api/search/text`
4. **Backend:** `api/routers/search.py` → `search_by_text()`
5. **Embedding:** `get_text_model()` → Generate embedding
6. **Search:** `api/search_utils.py` → `execute_vector_search()`
7. **Database:** PostgreSQL vector similarity search
8. **Results:** Return products with similarity scores
9. **Frontend:** `ResultsGrid.tsx` displays results

### Image Search Request:

1. **User Action:** Uploads image file
2. **Frontend:** `SearchInterface.tsx` → `handleImageUpload()`
3. **API Call:** `POST /api/search/image/upload` (FormData)
4. **Backend:** `search_by_image_upload()` → Process image
5. **Embedding:** `get_clip_model()` → Generate CLIP embedding
6. **Search:** Vector similarity search
7. **Results:** Visually similar products
8. **Frontend:** Display results

## 🎯 Key Files for Different Purposes

### To Understand Search:
1. `api/routers/search.py` - Search endpoints
2. `api/search_utils.py` - Search logic
3. `database/schema.sql` - Vector columns

### To Understand Frontend:
1. `frontend/app/page.tsx` - Main page
2. `frontend/components/SearchInterface.tsx` - User input
3. `frontend/components/ResultsGrid.tsx` - Results display

### To Understand AI/ML:
1. `embeddings/generate_clip_embeddings.py` - Image AI
2. `embeddings/generate_text_embeddings.py` - Text AI
3. `api/routers/search.py` - How AI is used

### To Understand Data:
1. `database/schema.sql` - Data structure
2. `database/import_products.py` - Data import
3. `metadata/extract_metadata.py` - Data enrichment

This guide explains every file in detail! 📚

