# Quick Reference Guide - Vibe Search

## 🚀 Start Here - Understanding Order

### Level 1: Overview (15 minutes)
1. Read `README.md` - What the project does
2. Read `SUMMARY.md` - Quick summary
3. Open `http://localhost:3000` - See it in action

### Level 2: Data Layer (30 minutes)
1. `database/schema.sql` - How data is stored
2. `database/import_products.py` - How data is loaded
3. `metadata/extract_metadata.py` - How metadata is extracted

### Level 3: AI/ML (45 minutes)
1. `embeddings/generate_clip_embeddings.py` - Image AI
2. `embeddings/generate_text_embeddings.py` - Text AI
3. Understand: Images/text → Numbers → Similarity

### Level 4: Backend (1 hour)
1. `api/main.py` - Application setup
2. `api/routers/search.py` - Search endpoints
3. `api/search_utils.py` - Search logic

### Level 5: Frontend (45 minutes)
1. `frontend/app/page.tsx` - Main page
2. `frontend/components/SearchInterface.tsx` - User input
3. `frontend/components/ResultsGrid.tsx` - Results

### Level 6: Scraping (30 minutes)
1. `scrapers/base_scraper.py` - Base functionality
2. `scrapers/pinterest_scraper.py` - Pinterest scraper

## 📁 Essential Files to Understand

### Must Read (Core Functionality):
1. `database/schema.sql` - Data structure
2. `api/routers/search.py` - Search implementation
3. `api/search_utils.py` - Vector search
4. `frontend/app/page.tsx` - Main UI

### Should Read (Important):
1. `embeddings/generate_clip_embeddings.py` - AI component
2. `frontend/components/SearchInterface.tsx` - User interaction
3. `api/main.py` - Application setup

### Good to Read (Supporting):
1. `database/import_products.py` - Data import
2. `metadata/extract_metadata.py` - Data enrichment
3. `scrapers/pinterest_scraper.py` - Data collection

## 🔑 Key Concepts (One Sentence Each)

- **Vector Embedding**: Converting images/text to numbers for similarity comparison
- **CLIP**: AI model that understands images semantically
- **Sentence Transformer**: AI model that understands text meaning
- **pgvector**: PostgreSQL extension for storing and searching vectors
- **Cosine Similarity**: Mathematical way to measure how similar two vectors are
- **Multimodal Search**: Searching using both text and images
- **HNSW Index**: Fast approximate nearest neighbor search algorithm

## 🔄 Request Flow (Quick)

**Text Search:**
User → Frontend → API → Generate Embedding → Database Search → Results

**Image Search:**
User → Frontend → API → CLIP Embedding → Database Search → Results

## 📊 Project Stats

- **491 products** in database
- **487** with image embeddings
- **491** with text embeddings
- **5 API endpoints**
- **4 frontend components**
- **3 main layers**: Frontend, Backend, Database

## 🎯 File Purpose Quick Look

| File | Purpose | Key Function |
|------|---------|--------------|
| `schema.sql` | Database structure | Defines tables and indexes |
| `import_products.py` | Load data | Imports CSV to database |
| `generate_clip_embeddings.py` | Image AI | Creates image vectors |
| `generate_text_embeddings.py` | Text AI | Creates text vectors |
| `extract_metadata.py` | Data enrichment | Extracts colors/styles |
| `api/main.py` | App setup | Creates FastAPI app |
| `api/routers/search.py` | Search API | Handles search requests |
| `api/search_utils.py` | Search logic | Vector similarity search |
| `frontend/app/page.tsx` | Main page | Coordinates components |
| `SearchInterface.tsx` | User input | Handles search forms |
| `ResultsGrid.tsx` | Results display | Shows search results |
| `pinterest_scraper.py` | Data collection | Scrapes Pinterest |

## 💡 Explaining to Others

### 30-Second Version:
"Vibe Search uses AI to find fashion products. You can search with text like 'black sneakers' or upload an image to find visually similar products. It uses vector embeddings and similarity search."

### 2-Minute Version:
"Vibe Search is a multimodal fashion search engine. It converts product images and text into numerical vectors using AI models (CLIP for images, sentence transformers for text). When you search, it finds products with similar vectors using PostgreSQL's pgvector extension. The system has a FastAPI backend, Next.js frontend, and stores 491 products with embeddings."

### 5-Minute Version:
[Use EXPLANATION_TEMPLATE.md]

## 🎓 Study Checklist

- [ ] Understand what the project does
- [ ] Understand database structure
- [ ] Understand how embeddings work
- [ ] Understand search flow
- [ ] Understand frontend structure
- [ ] Can trace a search request end-to-end
- [ ] Can explain to someone else

## 🔍 Debugging Guide

**Frontend not loading?**
→ Check `frontend/app/page.tsx` for errors
→ Check browser console (F12)

**Search not working?**
→ Check backend is running
→ Check database connection
→ Check `api/routers/search.py`

**No results?**
→ Check embeddings exist
→ Check `embeddings/check_embedding_status.py`
→ Check database has products

**API errors?**
→ Check `api/main.py` for CORS
→ Check `api/database.py` for connection
→ Check logs in terminal

## 📚 Documentation Files

- `PROJECT_ROADMAP.md` - Complete learning path
- `FILE_BY_FILE_GUIDE.md` - Every file explained
- `EXPLANATION_TEMPLATE.md` - How to explain
- `ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- `QUICK_REFERENCE.md` - This file

## 🎯 Next Steps

1. **Read PROJECT_ROADMAP.md** - Follow the learning path
2. **Read FILE_BY_FILE_GUIDE.md** - Understand each file
3. **Use EXPLANATION_TEMPLATE.md** - Prepare your explanation
4. **Study ARCHITECTURE_DIAGRAM.md** - Visualize the system

You're ready to explain the entire project! 🚀

