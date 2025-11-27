# Vibe Search - Multimodal Fashion Search Engine

A full-stack multimodal search engine that combines visual AI, natural language processing, and vector search for fashion product discovery. Search products using images, natural language queries, or both.

![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20Next.js%20%2B%20PostgreSQL-blue)
![AI](https://img.shields.io/badge/AI-CLIP%20%2B%20YOLO%20%2B%20Sentence%20Transformers-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-orange)

## 🚀 Features

### Core Search
- **Visual Search**: Upload an image and find visually similar products using CLIP embeddings (512-dim)
- **Text Search**: Natural language queries with semantic understanding (384-dim embeddings)
- **Hybrid Search**: Combines vector similarity with keyword matching for better relevance
- **Natural Language Parsing**: Understands queries like "black sneakers under $50 but not boots"

### AI-Powered Features
- **Negative Filtering**: "similar items but NOT sneakers" excludes specific items
- **Price Extraction**: "under $50", "over $100", "$25-75" parsed automatically
- **Category Detection**: Automatic category extraction from queries
- **Quality Filtering**: Blur detection, NSFW filtering, resolution checks

### Web Scraping + AI Processing
- **Pinterest & Instagram Scrapers**: Automated fashion image collection
- **AI Processing Pipeline**: 
  - Quality filtering (blur, NSFW, brightness)
  - Object detection (YOLOv8 for fashion items)
  - CLIP embedding generation
  - Color extraction (K-means clustering)
  - Metadata extraction (styles, brands)

### Frontend
- **Modern UI**: Next.js 14+ with TypeScript and Tailwind CSS
- **Image Upload**: Drag & drop or click to upload
- **Real-time Search**: Instant results with similarity scores
- **Explore Feed**: Browse AI-processed scraped images

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 3000)                      │
│  Next.js + React + TypeScript + Tailwind CSS                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ SearchInterface│  │  ResultsGrid   │  │ ExploreFeed  │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Port 8000)                       │
│  FastAPI + Python                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Query Parser  │  │ Search Utils   │  │  AI Models   │  │
│  │  - Categories  │  │ - Vector Search│  │  - CLIP      │  │
│  │  - Negatives   │  │ - Hybrid Search│  │  - YOLO      │  │
│  │  - Price       │  │ - Filters      │  │  - SentTrans │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ SQL + Vector Queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (Port 5432)                      │
│  PostgreSQL 18 + pgvector                                    │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │    products    │  │ scraped_images │                     │
│  │  - 491 items   │  │ - AI processed │                     │
│  │  - Embeddings  │  │ - Embeddings   │                     │
│  │  - Metadata    │  │ - Detections   │                     │
│  └────────────────┘  └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
CultureCircleTask/
├── api/                          # FastAPI Backend
│   ├── main.py                   # Application entry point
│   ├── database.py               # Database connection
│   ├── models.py                 # Pydantic schemas
│   ├── query_parser.py           # Natural language parsing
│   ├── search_utils.py           # Vector search logic
│   └── routers/
│       ├── search.py             # Search endpoints
│       ├── feed.py               # Scraped images feed
│       └── health.py             # Health check
│
├── ai/                           # AI/ML Modules
│   ├── clip_embedding.py         # CLIP model integration
│   ├── object_detector.py        # YOLO object detection
│   ├── quality_filter.py         # Image quality filtering
│   ├── metadata_extractor.py     # Color/style extraction
│   └── processing_pipeline.py    # AI workflow orchestration
│
├── scrapers/                     # Web Scrapers
│   ├── base_scraper.py           # Base class with DB ops
│   ├── pinterest_scraper.py      # Pinterest scraper
│   ├── instagram_scraper.py      # Instagram scraper
│   └── run_scrapers.py           # CLI runner
│
├── database/                     # Database Scripts
│   ├── schema.sql                # Main schema
│   ├── schema_update_scraped_images.sql  # AI fields migration
│   ├── setup_database.py         # Schema setup
│   └── import_products.py        # CSV import
│
├── embeddings/                   # Batch Processing
│   ├── generate_clip_embeddings.py   # Image embeddings
│   └── generate_text_embeddings.py   # Text embeddings
│
├── frontend/                     # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx              # Main page
│   │   └── layout.tsx            # App layout
│   ├── components/
│   │   ├── SearchInterface.tsx   # Search UI
│   │   ├── ResultsGrid.tsx       # Results display
│   │   └── ExploreFeed.tsx       # Scraped images feed
│   └── types/
│       └── index.ts              # TypeScript interfaces
│
├── run_server.py                 # Start backend
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 18+ with pgvector extension

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..

# Install Playwright browsers (for scraping)
playwright install chromium
```

### 2. Setup Database

```bash
# Create database and enable pgvector
psql -U postgres
CREATE DATABASE vibe_search;
\c vibe_search
CREATE EXTENSION vector;
\q

# Setup schema
python database/setup_database.py

# Import products
python database/import_products.py
```

### 3. Generate Embeddings

```bash
# Generate CLIP embeddings for product images
python embeddings/generate_clip_embeddings.py

# Generate text embeddings for product titles
python embeddings/generate_text_embeddings.py
```

### 4. Start the Application

```bash
# Terminal 1: Start Backend
python run_server.py
# Backend runs on http://localhost:8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```

### Text Search
```http
POST /api/search/text
Content-Type: application/json

{
  "query": "black sneakers under $50 but not boots",
  "limit": 20,
  "category": "Footwear",
  "brand": "Nike",
  "min_price": 0,
  "max_price": 50,
  "colors": ["black"],
  "gender": "male"
}
```

### Image Upload Search
```http
POST /api/search/image/upload
Content-Type: multipart/form-data

image_file: <file>
text_query: "similar items"
limit: 20
```

### Image URL Search
```http
POST /api/search/image
Content-Type: application/json

{
  "image_url": "https://example.com/shoe.jpg",
  "limit": 20
}
```

### Scraped Images Feed
```http
GET /api/feed/scraped?limit=20&offset=0
```

---

## 🔍 Natural Language Query Examples

The query parser understands:

| Query | Parsed Result |
|-------|---------------|
| "black sneakers under $50" | category: shoes, max_price: 50, keywords: [black, sneakers] |
| "similar outfit but not shoes" | exclude_categories: [shoes] |
| "luxury watch $100-500" | min_price: 100, max_price: 500 |
| "show me tops but no hoodies" | category: tops, exclude_keywords: [hoodies] |
| "items over $200" | min_price: 200 |

---

## 🕷️ Web Scraping

### Run Pinterest Scraper
```bash
# Scrape 50 images from Pinterest
python scrapers/run_scrapers.py --source pinterest --limit 50

# Fast mode (shorter delays)
python scrapers/run_scrapers.py --source pinterest --limit 10 --fast
```

### Run Instagram Scraper
```bash
python scrapers/run_scrapers.py --source instagram --limit 50
```

### AI Processing Pipeline
Each scraped image goes through:
1. **Quality Filter**: Reject blurry, NSFW, low-resolution images
2. **Object Detection**: YOLO identifies fashion items (shoes, tops, etc.)
3. **CLIP Embedding**: Generate 512-dim visual embedding
4. **Color Extraction**: K-means clustering for dominant colors
5. **Metadata Extraction**: Extract styles and brands

---

## 🗄️ Database Schema

### Products Table
```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category VARCHAR(100),
    sub_category VARCHAR(100),
    brand_name VARCHAR(100),
    lowest_price DECIMAL(10, 2),
    featured_image TEXT,
    image_embedding vector(512),    -- CLIP embedding
    text_embedding vector(384),     -- Sentence transformer
    extracted_colors TEXT[],
    extracted_styles TEXT[],
    is_active BOOLEAN DEFAULT TRUE
);
```

### Scraped Images Table
```sql
CREATE TABLE scraped_images (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    image_url TEXT NOT NULL,
    caption TEXT,
    image_embedding vector(512),
    detected_class VARCHAR(100),    -- YOLO detection
    bbox INTEGER[],                 -- Bounding box
    extracted_colors TEXT[],
    extracted_styles TEXT[],
    quality_score JSONB,
    UNIQUE(source, image_url)
);
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vibe_search
DB_USER=postgres
POSTGRES_PASSWORD=postgres

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Current Status

- ✅ Database schema with pgvector
- ✅ Product data import (491 products)
- ✅ CLIP image embeddings (512-dim)
- ✅ Text embeddings (384-dim)
- ✅ FastAPI backend with search endpoints
- ✅ Natural language query parsing
- ✅ Hybrid search (vector + keyword)
- ✅ Negative filtering ("not shoes")
- ✅ Price extraction from queries
- ✅ Pinterest scraper with AI processing
- ✅ Instagram scraper with AI processing
- ✅ Next.js frontend with search UI
- ✅ Explore feed for scraped images

---

## 🧪 Testing

```bash
# Test API health
curl http://localhost:8000/api/health

# Test text search
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "black sneakers under $50", "limit": 5}'

# Test query parser
python -c "from api.query_parser import QueryParser; p = QueryParser(); print(p.parse('black sneakers under \$50 but not boots'))"
```

---

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **Architecture**: `ARCHITECTURE_DIAGRAM.md`
- **Interview Prep**: `INTERVIEW_ROADMAP.md`
- **Demo Guide**: `PROJECT_EXPLANATION_GUIDE.md`
- **Quick Demo**: `QUICK_DEMO_CHECKLIST.md`

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **psycopg2**: PostgreSQL database driver
- **Pydantic**: Data validation and schemas

### AI/ML
- **CLIP** (OpenAI): Visual embeddings (512-dim)
- **Sentence Transformers**: Text embeddings (384-dim)
- **YOLOv8**: Object detection for fashion items
- **OpenCV**: Image processing and quality metrics
- **NudeNet**: NSFW detection

### Database
- **PostgreSQL 18**: Relational database
- **pgvector**: Vector similarity search extension
- **HNSW Index**: Fast approximate nearest neighbor search

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Icon library

### Scraping
- **Playwright**: Browser automation
- **BeautifulSoup**: HTML parsing

---

## 🙏 Acknowledgments

- [OpenAI CLIP](https://github.com/openai/CLIP) for visual embeddings
- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [pgvector](https://github.com/pgvector/pgvector) for vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8

---

## 📄 License

This project is part of a technical assessment for Culture Circle.

---

## 🚀 Quick Demo

1. Start both servers (backend + frontend)
2. Open http://localhost:3000
3. Try text search: "black sneakers under $50 but not boots"
4. Try image search: upload any fashion image
5. Explore the feed: view AI-processed scraped images

**That's Vibe Search - Multimodal AI-powered fashion search!**
