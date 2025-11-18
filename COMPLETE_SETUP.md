# Complete Setup Guide - All Steps

This guide walks through **every step** to get Vibe Search fully operational.

## Prerequisites Check

```bash
# Check Python (need 3.11+)
python --version

# Check Node.js (need 18+)
node --version

# Check PostgreSQL (need 18+)
psql --version
```

## Step-by-Step Setup

### 1. Python Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 3. Database Setup (WSL/PostgreSQL)

#### In WSL Terminal:

```bash
# Start PostgreSQL
sudo service postgresql start

# Connect to PostgreSQL
sudo -u postgres psql

# In psql:
CREATE DATABASE vibe_search;
\c vibe_search
CREATE EXTENSION vector;
\q
```

#### Configure PostgreSQL for Windows Access:

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/18/main/postgresql.conf
# Set: listen_addresses = 'localhost'

# Edit pg_hba.conf
sudo nano /etc/postgresql/18/main/pg_hba.conf
# Add:
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# Restart PostgreSQL
sudo service postgresql restart
```

### 4. Import Product Data

```bash
# Setup database schema
python database/setup_database.py

# Import products from CSV
python database/import_products.py
```

### 5. Generate Embeddings

```bash
# Generate CLIP embeddings (takes time, ~2-3 hours for all)
python embeddings/generate_clip_embeddings.py

# Generate text embeddings (fast, ~1 minute)
python embeddings/generate_text_embeddings.py
```

### 6. Extract Metadata

```bash
# Extract colors, styles, brands from titles
python metadata/extract_metadata.py
```

### 7. Run Scrapers (Optional)

```bash
# Scrape Pinterest images
python scrapers/run_scrapers.py --source pinterest --limit 50
```

### 8. Start Backend

```bash
# Start FastAPI server
python run_server.py

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 9. Start Frontend

```bash
# In a new terminal
cd frontend
npm run dev

# Frontend runs on http://localhost:3000
```

### 10. Test Everything

```bash
# Test database (in another terminal)
python tests/test_database.py

# Test API (make sure backend is running)
python tests/test_api.py
```

## Verification Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Can search with text query
- [ ] Can upload image for search
- [ ] Results display with match scores
- [ ] Product modals work
- [ ] Explore feed shows scraped images (if any)

## Troubleshooting

### Database Connection Issues

**Problem**: "Connection refused" or "password authentication failed"

**Solutions**:
1. Make sure PostgreSQL is running: `sudo service postgresql status`
2. Check pg_hba.conf allows connections from localhost
3. Verify password in environment variables
4. Test connection: `psql -U postgres -h localhost -d vibe_search`

### Frontend Can't Connect to API

**Problem**: CORS errors or connection refused

**Solutions**:
1. Make sure backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Verify CORS settings in `api/main.py`

### Embedding Generation Fails

**Problem**: Model download fails or out of memory

**Solutions**:
1. Check internet connection
2. Ensure enough disk space (~2GB for models)
3. Try with smaller limit: `python embeddings/generate_clip_embeddings.py 10`
4. Use CPU (default) - GPU optional

## Quick Commands Reference

```bash
# Start everything
python run_server.py          # Terminal 1
cd frontend && npm run dev    # Terminal 2

# Test everything
python tests/test_database.py
python tests/test_api.py

# Check status
python embeddings/check_embedding_status.py
```

## Next Steps After Setup

1. **Scrape More Images**: Run scrapers to populate explore feed
2. **Test Search**: Try various queries and images
3. **Customize**: Modify filters, add features
4. **Deploy**: See SHARING.md for deployment options

## Project is Ready! 🎉

Once all steps are complete, your Vibe Search application is fully operational!

