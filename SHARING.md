# How to Share This Project

This guide explains different ways to share your Vibe Search project with others.

## 📦 Method 1: GitHub Repository (Recommended)

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name it (e.g., "vibe-search")
4. Choose public or private
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Initialize Git (if not done)

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Vibe Search MVP"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/vibe-search.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Share the Repository

Share the repository URL:
```
https://github.com/YOUR_USERNAME/vibe-search
```

## 📁 Method 2: ZIP Archive

### Create Archive

**Windows (PowerShell):**
```powershell
# Exclude unnecessary files
$exclude = @('.venv', '__pycache__', '*.pyc', '.git', 'node_modules', '.next')
Compress-Archive -Path . -DestinationPath vibe-search.zip -Exclude $exclude
```

**Linux/Mac:**
```bash
zip -r vibe-search.zip . \
  -x "*.venv/*" \
  -x "*__pycache__/*" \
  -x "*.pyc" \
  -x "*.git/*" \
  -x "*node_modules/*" \
  -x "*.next/*"
```

### Share the ZIP File

- Upload to Google Drive, Dropbox, or similar
- Email the file (if small enough)
- Share via file sharing service

## 🐳 Method 3: Docker (For Deployment)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run_server.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=vibe_search
      - DB_USER=postgres
      - POSTGRES_PASSWORD=postgres
    depends_on:
      - db

  db:
    image: pgvector/pgvector:pg18
    environment:
      - POSTGRES_DB=vibe_search
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Share Docker Setup

```bash
# Build and run
docker-compose up -d

# Share the docker-compose.yml and Dockerfile
```

## 📋 Method 4: Documentation Package

Create a comprehensive package with:

1. **README.md** (already created)
2. **SETUP.md** - Detailed setup instructions
3. **API_DOCS.md** - API documentation
4. **ARCHITECTURE.md** - System architecture
5. **DEMO.md** - Demo instructions

### Create SETUP.md

```markdown
# Setup Guide

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Setup database: `python database/setup_database.py`
3. Import data: `python database/import_products.py`
4. Generate embeddings: `python embeddings/generate_clip_embeddings.py`
5. Start server: `python run_server.py`
```

## 🔗 Method 5: Live Demo

### Deploy to Cloud

**Option A: Heroku**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python run_server.py" > Procfile

# Deploy
heroku create vibe-search
git push heroku main
```

**Option B: Railway**
```bash
# Connect GitHub repo to Railway
# Railway auto-detects Python projects
```

**Option C: Render**
```bash
# Connect GitHub repo to Render
# Configure build and start commands
```

### Share Demo URL

Once deployed, share the live URL:
```
https://your-app.herokuapp.com
```

## 📝 What to Include When Sharing

### Essential Files:
- ✅ `README.md` - Project overview
- ✅ `requirements.txt` - Python dependencies
- ✅ `database/schema.sql` - Database schema
- ✅ Source code (all `.py` files)
- ✅ Configuration files

### Optional but Helpful:
- ✅ `.env.example` - Example environment variables
- ✅ `docker-compose.yml` - Docker setup
- ✅ `SHARING.md` - This file
- ✅ Screenshots/demo videos
- ✅ Architecture diagrams

### Exclude:
- ❌ `.venv/` - Virtual environment
- ❌ `__pycache__/` - Python cache
- ❌ `.git/` - Git history (unless sharing via Git)
- ❌ `node_modules/` - Node dependencies
- ❌ `.env` - Environment variables with secrets
- ❌ Large model files (if any)

## 🎥 Creating a Demo Video

1. **Record Screen** using:
   - OBS Studio (free)
   - Windows Game Bar (Win+G)
   - QuickTime (Mac)

2. **Show**:
   - Project structure
   - Database setup
   - Running the API
   - Testing search endpoints
   - Frontend (when ready)

3. **Keep it under 5 minutes** (as per requirements)

## 📧 Sharing Checklist

Before sharing, ensure:

- [ ] README.md is complete and clear
- [ ] All dependencies are listed in requirements.txt
- [ ] Database setup instructions are clear
- [ ] API endpoints are documented
- [ ] Example requests/responses are provided
- [ ] Environment variables are documented
- [ ] No sensitive data (passwords, API keys) in code
- [ ] .gitignore is properly configured
- [ ] Code is commented and readable

## 🚀 Quick Share Commands

```bash
# Create a shareable package
# 1. Clean up
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 2. Create archive
zip -r vibe-search-shareable.zip . \
  -x "*.venv/*" \
  -x "*.git/*" \
  -x "*node_modules/*" \
  -x "*.next/*" \
  -x "*.env"

# 3. Share!
```

## 💡 Tips

1. **For GitHub**: Use clear commit messages and organize commits logically
2. **For ZIP**: Include a setup guide in the root directory
3. **For Docker**: Test the Docker setup before sharing
4. **For Demo**: Record a short video showing key features
5. **Always**: Test the setup on a fresh machine if possible

