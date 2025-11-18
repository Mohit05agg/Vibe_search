# Vibe_search

# Vibe Search - Multimodal Fashion Search Engine

A full-stack multimodal search engine that combines visual and text-based product discovery for fashion and lifestyle items. Similar to the Shoppin app, allowing users to search products using either images or natural language queries.

## 🚀 Features

- **Visual Search**: Upload an image and find similar products using CLIP embeddings
- **Text Search**: Natural language queries with semantic understanding
- **Metadata Extraction**: Automatic extraction of brands, colors, and styles from product titles
- **Web Scraping**: Collects fashion images from Pinterest and Instagram
- **Vector Database**: PostgreSQL with pgvector for efficient similarity search
- **RESTful API**: FastAPI backend with comprehensive search endpoints
- **Modern Frontend**: Next.js 14+ with Tailwind CSS and shadcn/ui (coming soon)

## 📋 Project Structure

```
CultureCircleTask/
├── api/                    # FastAPI backend
│   ├── main.py            # Main application
│   ├── routers/           # API routes
│   ├── models.py          # Pydantic models
│   └── search_utils.py    # Search utilities
├── database/              # Database scripts
│   ├── schema.sql         # Database schema
│   ├── import_products.py # CSV import script
│   └── setup_database.py  # Database setup
├── embeddings/            # Embedding generation
│   ├── generate_clip_embeddings.py
│   └── generate_text_embeddings.py
├── metadata/              # Metadata extraction
│   └── extract_metadata.py
├── scrapers/              # Web scrapers
│   ├── pinterest_scraper.py
│   ├── instagram_scraper.py
│   └── run_scrapers.py
├── products_export_*.csv  # Product data
└── requirements.txt       # Python dependencies
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 18+ (with pgvector extension)
- WSL (Windows Subsystem for Linux) for PostgreSQL on Windows

### 1. Environment Setup

#### Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Install PostgreSQL with pgvector (WSL)

```bash
# In WSL terminal
sudo apt update
sudo apt install postgresql-18 postgresql-contrib-18 -y
sudo apt install build-essential git postgresql-server-dev-18 -y

# Install pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
sudo service postgresql restart

# Create database
sudo -u postgres psql
CREATE DATABASE vibe_search;
\c vibe_search
CREATE EXTENSION vector;
```

### 2. Database Setup

```bash
# Setup database schema
python database/setup_database.py

# Import product data
python database/import_products.py
```

### 3. Generate Embeddings

```bash
# Generate CLIP embeddings for images
python embeddings/generate_clip_embeddings.py

# Generate text embeddings
python embeddings/generate_text_embeddings.py
```

### 4. Extract Metadata

```bash
# Extract colors, styles, brands from product titles
python metadata/extract_metadata.py
```

### 5. Run Scrapers

```bash
# Scrape Pinterest and Instagram
python scrapers/run_scrapers.py

# Or scrape specific source
python scrapers/run_scrapers.py --source pinterest --limit 50
```

### 6. Start Backend API

```bash
# Start FastAPI server
python run_server.py

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Image Search
```
POST /api/search/image
Body: {
  "image_url": "https://example.com/image.jpg",
  "limit": 20,
  "category": "Apparel",
  "brand": "Nike",
  "min_price": 0,
  "max_price": 1000,
  "colors": ["black", "white"],
  "gender": "male"
}
```

### Text Search
```
POST /api/search/text
Body: {
  "query": "beach shorts for summer",
  "limit": 20,
  "category": "Apparel",
  "brand": "Adidas",
  "min_price": 0,
  "max_price": 500,
  "colors": ["blue"],
  "gender": "unisex"
}
```

## 🎯 Target Boards/Pages

### Pinterest Boards
- Minimal Streetwear
- Men's Streetwear Outfit Ideas
- Streetwear Outfit Ideas
- Streetwear Fashion Instagram
- Luxury Fashion
- Luxury Classy Outfits
- Luxury Streetwear Brands

### Instagram Pages
- @minimalstreetstyle
- @outfitgrid
- @outfitpage
- @mensfashionpost
- @stadiumgoods
- @flightclub
- @hodinkee
- @wristcheck
- @purseblog
- @sunglasshut
- @rayban
- @prada
- @cartier
- @thesolesupplier

## 📦 Sharing the Project

### Option 1: GitHub Repository

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit: Vibe Search MVP"
```

2. **Create .gitignore**:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Database
*.db
*.sqlite

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Node
node_modules/
.next/
out/
dist/

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

3. **Push to GitHub**:
```bash
# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/vibe-search.git
git branch -M main
git push -u origin main
```

### Option 2: Docker Deployment

Create `Dockerfile` and `docker-compose.yml` for easy deployment:

```bash
# Build and run with Docker
docker-compose up -d
```

### Option 3: Export as ZIP

```bash
# Create archive excluding unnecessary files
# On Windows:
Compress-Archive -Path . -DestinationPath vibe-search.zip -Exclude @('.venv','__pycache__','*.pyc','.git')
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

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

## 📊 Current Status

- ✅ Database schema with pgvector
- ✅ Product data import (491 products)
- ✅ Metadata extraction (colors, styles, brands)
- ✅ CLIP embeddings (487 products)
- ✅ Text embeddings (491 products)
- ✅ FastAPI backend with search endpoints
- ✅ Pinterest scraper (working)
- ✅ Instagram scraper (limited by anti-bot measures)
- 🚧 Next.js frontend (in progress)

## 🧪 Testing

```bash
# Test scrapers
python scrapers/test_scraper.py

# Test API (after starting server)
curl http://localhost:8000/api/health

# Test search
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "black sneakers", "limit": 5}'
```

## 📝 Documentation

- API Documentation: http://localhost:8000/docs (when server is running)
- Database Schema: `database/schema.sql`
- Scraper README: `scrapers/README.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of a technical assessment.

## 🙏 Acknowledgments

- OpenAI CLIP for visual embeddings
- Sentence Transformers for text embeddings
- pgvector for vector similarity search
- FastAPI for the backend framework

