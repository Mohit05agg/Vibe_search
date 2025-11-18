# Vibe Search - Complete Project Roadmap & Explanation Guide

## 🎯 Project Overview

**Vibe Search** is a multimodal fashion search engine that allows users to:
- Search products using **text queries** (e.g., "black sneakers")
- Search products using **images** (upload an image, find similar products)
- Browse **scraped fashion images** from Pinterest/Instagram
- View **product details** with similarity scores

## 📚 Learning Path - Start Here!

### Phase 1: Understanding the Big Picture (30 minutes)

**Goal:** Understand what the project does and how components connect

1. **Read this first:**
   - `README.md` - Project overview and features
   - `SUMMARY.md` - Quick project summary
   - `PROJECT_STATUS.md` - What's completed

2. **Key Concepts to Understand:**
   - **Multimodal Search**: Using both text and images to search
   - **Vector Embeddings**: Converting images/text to numbers for similarity search
   - **pgvector**: PostgreSQL extension for storing and searching vectors
   - **CLIP**: AI model that understands images and text together
   - **FastAPI**: Modern Python web framework for APIs
   - **Next.js**: React framework for frontend

### Phase 2: Database & Data Layer (1-2 hours)

**Goal:** Understand how data is stored and processed

#### Step 1: Database Schema
**File:** `database/schema.sql`

**What it does:**
- Defines database structure
- Creates tables: `products` and `scraped_images`
- Sets up pgvector extension
- Creates indexes for fast searching

**Key Concepts:**
- `vector(512)` - Stores CLIP embeddings (512 numbers)
- `vector(384)` - Stores text embeddings (384 numbers)
- `HNSW index` - Fast approximate nearest neighbor search
- Arrays (`TEXT[]`) - Stores multiple colors/styles

**Read order:**
1. Look at table structure
2. Understand vector columns
3. See indexes for performance

#### Step 2: Data Import
**File:** `database/import_products.py`

**What it does:**
- Reads CSV file with product data
- Converts data types (strings to numbers, booleans)
- Inserts into PostgreSQL database
- Handles errors and duplicates

**Key Functions:**
- `parse_bool()` - Converts "True"/"False" strings
- `parse_decimal()` - Converts price strings
- `import_products_from_csv()` - Main import function

**How to understand:**
1. See how CSV columns map to database columns
2. Understand data type conversions
3. Learn batch insertion for efficiency

#### Step 3: Metadata Extraction
**File:** `metadata/extract_metadata.py`

**What it does:**
- Extracts colors from product titles (e.g., "Green T-Shirt" → ["Green"])
- Extracts styles (e.g., "Casual", "Formal")
- Extracts brands from titles
- Stores in database arrays

**Key Functions:**
- `extract_colors()` - Finds color names in text
- `extract_styles()` - Finds style keywords
- `extract_brand_from_title()` - Gets brand name

**How to understand:**
1. See the color/style keyword lists
2. Understand regex pattern matching
3. Learn how metadata improves search

### Phase 3: AI/ML Layer - Embeddings (2-3 hours)

**Goal:** Understand how AI models create searchable vectors

#### Step 1: Image Embeddings (CLIP)
**File:** `embeddings/generate_clip_embeddings.py`

**What it does:**
- Downloads product images from URLs
- Uses CLIP model to convert images to 512-dimensional vectors
- Stores vectors in database for similarity search

**Key Concepts:**
- **CLIP Model**: Understands images semantically
- **Embedding**: Image converted to numbers (vector)
- **Normalization**: Makes vectors comparable
- **Batch Processing**: Processes multiple images efficiently

**How to understand:**
1. See how images are downloaded
2. Understand CLIP model loading
3. Learn vector generation process
4. See how vectors are stored in database

**Flow:**
```
Product Image URL → Download Image → CLIP Model → 512 numbers → Database
```

#### Step 2: Text Embeddings
**File:** `embeddings/generate_text_embeddings.py`

**What it does:**
- Takes product titles/descriptions
- Uses sentence-transformers to create 384-dimensional vectors
- Stores for semantic text search

**Key Concepts:**
- **Sentence Transformers**: Understands text meaning
- **Semantic Search**: Finds meaning, not just keywords
- **Query Expansion**: "beach shorts" matches "swim trunks"

**How to understand:**
1. See how text is encoded
2. Understand semantic understanding
3. Learn how queries match products

### Phase 4: Backend API (2-3 hours)

**Goal:** Understand the REST API that powers search

#### Step 1: Main Application
**File:** `api/main.py`

**What it does:**
- Creates FastAPI application
- Configures CORS (allows frontend to connect)
- Registers all API routes
- Root endpoint

**Key Concepts:**
- **FastAPI**: Modern Python web framework
- **CORS**: Cross-Origin Resource Sharing
- **Routers**: Organizes endpoints

**How to understand:**
1. See app initialization
2. Understand CORS configuration
3. See how routers are included

#### Step 2: Data Models
**File:** `api/models.py`

**What it does:**
- Defines request/response structures
- Validates data with Pydantic
- Type safety for API

**Key Models:**
- `ProductResponse` - What products look like in API
- `SearchResponse` - Search results format
- `ImageSearchRequest` - Image search parameters
- `TextSearchRequest` - Text search parameters

**How to understand:**
1. See request structure (what frontend sends)
2. See response structure (what API returns)
3. Understand validation rules

#### Step 3: Search Endpoints
**File:** `api/routers/search.py`

**What it does:**
- Handles image search requests
- Handles text search requests
- Generates embeddings for queries
- Returns similar products

**Key Functions:**
- `search_by_image()` - Image search endpoint
- `search_by_text()` - Text search endpoint
- `get_clip_model()` - Loads CLIP (lazy loading)
- `get_text_model()` - Loads sentence transformer

**How to understand:**
1. See how image uploads are handled
2. Understand embedding generation for queries
3. Learn how similarity search works
4. See filtering logic

**Flow for Image Search:**
```
User uploads image → CLIP embedding → Vector search in DB → Similar products → Return results
```

**Flow for Text Search:**
```
User types query → Text embedding → Vector search in DB → Similar products → Return results
```

#### Step 4: Search Utilities
**File:** `api/search_utils.py`

**What it does:**
- Builds SQL queries with filters
- Executes vector similarity search
- Combines filters with vector search

**Key Functions:**
- `build_filter_query()` - Creates WHERE clause
- `execute_vector_search()` - Runs pgvector similarity search

**Key Concepts:**
- **Cosine Distance** (`<=>`): Measures vector similarity
- **HNSW Index**: Fast approximate search
- **Filtering**: Category, brand, price, colors, gender

**How to understand:**
1. See how filters are built
2. Understand vector search SQL
3. Learn how similarity scores are calculated

#### Step 5: Database Connection
**File:** `api/database.py`

**What it does:**
- Creates database connections
- Manages connection pooling
- Provides cursor for queries

**How to understand:**
1. See connection configuration
2. Understand environment variables
3. Learn connection management

### Phase 5: Frontend (2-3 hours)

**Goal:** Understand the user interface

#### Step 1: Main Page
**File:** `frontend/app/page.tsx`

**What it does:**
- Main application page
- Manages state (search results, selected product)
- Coordinates components
- Handles image click-to-search

**Key State:**
- `searchResults` - Current search results
- `selectedProduct` - Product in detail modal
- `activeTab` - Which tab is shown

**How to understand:**
1. See component structure
2. Understand state management
3. Learn how components interact

#### Step 2: Search Interface
**File:** `frontend/components/SearchInterface.tsx`

**What it does:**
- Text search input
- Image upload interface
- Sends requests to backend API
- Shows loading states

**Key Functions:**
- `handleTextSearch()` - Text search handler
- `handleImageUpload()` - Image upload handler
- `handleFileChange()` - File selection

**How to understand:**
1. See form handling
2. Understand API calls
3. Learn file upload process

#### Step 3: Results Display
**File:** `frontend/components/ResultsGrid.tsx`

**What it does:**
- Displays search results in grid
- Shows product images, titles, prices
- Displays similarity scores
- Handles product clicks

**How to understand:**
1. See grid layout
2. Understand product card structure
3. Learn click handlers

#### Step 4: Explore Feed
**File:** `frontend/components/ExploreFeed.tsx`

**What it does:**
- Shows scraped images from Pinterest/Instagram
- Allows click-to-search
- Fetches images from backend

**How to understand:**
1. See image grid
2. Understand click-to-search
3. Learn API integration

#### Step 5: Product Modal
**File:** `frontend/components/ProductModal.tsx`

**What it does:**
- Shows detailed product information
- Displays in modal overlay
- Shows all product attributes

**How to understand:**
1. See modal structure
2. Understand product data display
3. Learn modal interactions

#### Step 6: Type Definitions
**File:** `frontend/types/index.ts`

**What it does:**
- Defines TypeScript types
- Ensures type safety
- Documents data structures

**Key Types:**
- `Product` - Product structure
- `SearchResponse` - API response format
- `ScrapedImage` - Scraped image structure

### Phase 6: Web Scraping (1-2 hours)

**Goal:** Understand how fashion images are collected

#### Step 1: Base Scraper
**File:** `scrapers/base_scraper.py`

**What it does:**
- Common functionality for all scrapers
- Rate limiting
- User agent rotation
- Database saving

**Key Features:**
- Random delays between requests
- Retry logic
- Error handling

#### Step 2: Pinterest Scraper
**File:** `scrapers/pinterest_scraper.py`

**What it does:**
- Scrapes Pinterest boards
- Extracts images, captions, hashtags
- Uses Playwright (browser automation)
- Saves to database

**How to understand:**
1. See browser automation
2. Understand page scrolling
3. Learn data extraction
4. See error handling

#### Step 3: Instagram Scraper
**File:** `scrapers/instagram_scraper.py`

**What it does:**
- Scrapes Instagram profiles
- Extracts posts and images
- Note: Limited by Instagram's anti-bot measures

**How to understand:**
1. See similar structure to Pinterest
2. Understand limitations
3. Learn why it may fail

### Phase 7: Testing & Quality (1 hour)

**Goal:** Understand how the project is tested

#### Test Files:
- `tests/test_database.py` - Database tests
- `tests/test_api.py` - API endpoint tests
- `test_full_project.py` - Complete project test

**What they test:**
- Database connectivity
- API endpoints
- Search functionality
- Performance
- Error handling

## 🔄 Complete Data Flow

### Text Search Flow:
```
User types query
  ↓
Frontend: SearchInterface.tsx
  ↓
API: POST /api/search/text
  ↓
Backend: search.py → get_text_model()
  ↓
Generate text embedding (384 numbers)
  ↓
Database: search_utils.py → execute_vector_search()
  ↓
PostgreSQL: Vector similarity search with pgvector
  ↓
Return similar products
  ↓
Frontend: ResultsGrid.tsx displays results
```

### Image Search Flow:
```
User uploads image
  ↓
Frontend: SearchInterface.tsx
  ↓
API: POST /api/search/image/upload
  ↓
Backend: search.py → get_clip_model()
  ↓
Generate image embedding (512 numbers)
  ↓
Database: Vector similarity search
  ↓
Return visually similar products
  ↓
Frontend: ResultsGrid.tsx displays results
```

### Scraping Flow:
```
Scraper: pinterest_scraper.py
  ↓
Playwright opens browser
  ↓
Navigates to Pinterest board
  ↓
Extracts images, captions, hashtags
  ↓
Saves to scraped_images table
  ↓
Frontend: ExploreFeed.tsx displays
  ↓
User clicks image → triggers image search
```

## 📁 File Organization Explained

### Root Level Files:
- `README.md` - Main documentation
- `requirements.txt` - Python dependencies
- `run_server.py` - Starts backend server
- `start_all.ps1` - Starts both servers
- `test_full_project.py` - Complete test suite

### Database Folder:
- `schema.sql` - Database structure
- `import_products.py` - CSV import script
- `setup_database.py` - Database setup

### API Folder:
- `main.py` - FastAPI application
- `models.py` - Data models
- `database.py` - DB connection
- `search_utils.py` - Search functions
- `routers/` - API endpoints

### Frontend Folder:
- `app/` - Next.js pages
- `components/` - React components
- `types/` - TypeScript definitions
- `package.json` - Node dependencies

### Embeddings Folder:
- `generate_clip_embeddings.py` - Image embeddings
- `generate_text_embeddings.py` - Text embeddings
- `check_embedding_status.py` - Status checker

### Scrapers Folder:
- `base_scraper.py` - Base class
- `pinterest_scraper.py` - Pinterest scraper
- `instagram_scraper.py` - Instagram scraper
- `run_scrapers.py` - Main scraper script

## 🎓 Learning Order Recommendation

### For Complete Beginners:
1. Read `README.md` (understand what it does)
2. Look at `database/schema.sql` (understand data structure)
3. Read `api/main.py` (see how API starts)
4. Check `frontend/app/page.tsx` (see frontend structure)
5. Trace a search request through the code

### For Understanding Architecture:
1. Start with database schema
2. Follow data import process
3. Understand embedding generation
4. See how API uses embeddings
5. Understand frontend integration

### For Explaining to Others:
1. Start with high-level overview
2. Show database structure
3. Demonstrate search flow
4. Show frontend interface
5. Explain AI/ML components

## 🔍 Key Files to Study First

**Must Understand:**
1. `database/schema.sql` - Data structure
2. `api/routers/search.py` - Core search logic
3. `api/search_utils.py` - Vector search
4. `frontend/app/page.tsx` - Main UI
5. `embeddings/generate_clip_embeddings.py` - AI component

**Good to Understand:**
1. `api/main.py` - Application setup
2. `frontend/components/SearchInterface.tsx` - User input
3. `scrapers/pinterest_scraper.py` - Data collection
4. `metadata/extract_metadata.py` - Data enrichment

**Reference:**
1. `api/models.py` - Data structures
2. `frontend/types/index.ts` - TypeScript types
3. `tests/` - How to test

## 💡 Key Concepts to Explain

### 1. Vector Embeddings
- Images/text converted to numbers
- Similar things have similar numbers
- Can measure similarity mathematically

### 2. Multimodal Search
- Search with text OR images
- Same underlying vector search
- Different embedding models

### 3. pgvector
- PostgreSQL extension
- Stores vectors efficiently
- Fast similarity search

### 4. CLIP Model
- Understands images semantically
- Trained on image-text pairs
- Can find visual similarity

### 5. FastAPI
- Modern Python web framework
- Automatic API documentation
- Type validation

### 6. Next.js
- React framework
- Server-side rendering
- Modern frontend development

## 📝 Explanation Template

When explaining the project:

1. **What it does:** Multimodal fashion search
2. **How it works:** Vector embeddings + similarity search
3. **Tech stack:** Python (FastAPI), TypeScript (Next.js), PostgreSQL
4. **Key innovation:** Combining visual and text search
5. **Data flow:** User → Frontend → API → Database → Results

## 🎯 Quick Reference

**To understand search:**
- Read `api/routers/search.py`
- See `api/search_utils.py`
- Check `database/schema.sql` for vector columns

**To understand frontend:**
- Start with `frontend/app/page.tsx`
- See `frontend/components/SearchInterface.tsx`
- Check `frontend/components/ResultsGrid.tsx`

**To understand data:**
- See `database/schema.sql`
- Check `database/import_products.py`
- Look at `embeddings/` folder

This roadmap will help you understand every part of the project! 🚀

