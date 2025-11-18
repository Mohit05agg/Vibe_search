# Quick Start Guide

Get Vibe Search up and running in minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 18+ with pgvector (or use Docker)

## Option 1: Automated Setup (Recommended)

### Windows
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Option 2: Manual Setup

### 1. Python Environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
```

### 2. Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Database Setup
```bash
# Make sure PostgreSQL is running
python database/setup_database.py
python database/import_products.py
```

### 4. Generate Embeddings
```bash
python embeddings/generate_clip_embeddings.py
python embeddings/generate_text_embeddings.py
```

### 5. Extract Metadata
```bash
python metadata/extract_metadata.py
```

## Running the Application

### Start Backend
```bash
python run_server.py
```
API will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Start Frontend (in new terminal)
```bash
cd frontend
npm run dev
```
Frontend will be available at: http://localhost:3000

## Testing

### Test API
```bash
# Make sure backend is running first
python tests/test_api.py
```

### Test Database
```bash
python tests/test_database.py
```

## Using Docker (Alternative)

```bash
docker-compose up -d
```

This will start both the API and database in containers.

## Troubleshooting

### Database Connection Issues
- Make sure PostgreSQL is running
- Check connection settings in `.env` or environment variables
- For WSL: Ensure PostgreSQL is configured to accept connections from Windows

### Frontend Not Connecting to API
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Make sure backend is running on the correct port
- Check CORS settings in `api/main.py`

### Embedding Generation Fails
- Check internet connection (models are downloaded from HuggingFace)
- Ensure enough disk space (models are ~600MB)
- Try running with smaller limit first: `python embeddings/generate_clip_embeddings.py 10`

## Next Steps

1. **Scrape Images**: `python scrapers/run_scrapers.py`
2. **Test Search**: Use the frontend or API docs
3. **Customize**: Modify filters, add features
4. **Deploy**: See `SHARING.md` for deployment options

## Support

- Check `README.md` for detailed documentation
- Review `PROJECT_STATUS.md` for current status
- See `SHARING.md` for deployment help

