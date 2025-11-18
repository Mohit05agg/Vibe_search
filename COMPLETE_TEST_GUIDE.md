# Complete Project Testing Guide

## Quick Start - Run Everything at Once

### Option 1: Use the Start Script (Easiest)

**Windows:**
```powershell
.\start_all.ps1
```
or
```cmd
start_all.bat
```

This will open two windows:
- Backend server (port 8000)
- Frontend server (port 3000)

### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```powershell
cd D:\CultureCircleTask
python run_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd D:\CultureCircleTask\frontend
npm run dev
```

## Testing Checklist

### ✅ Step 1: Verify Servers are Running

**Check Backend:**
- Visit: http://localhost:8000/docs
- Should show FastAPI Swagger documentation
- Try the "GET /api/health" endpoint

**Check Frontend:**
- Visit: http://localhost:3000
- Should show Vibe Search homepage
- Should see search interface

### ✅ Step 2: Test Backend API

#### Test Health Endpoint
```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

Or visit: http://localhost:8000/api/health

#### Test Text Search
```powershell
$body = @{
    query = "black sneakers"
    limit = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/search/text" -Method Post -Body $body -ContentType "application/json"
```

#### Test Image Search
```powershell
$body = @{
    image_url = "https://images.stockx.com/images/Nike-Air-Max-90-Black-White.jpg"
    limit = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/search/image" -Method Post -Body $body -ContentType "application/json"
```

### ✅ Step 3: Test Frontend

1. **Open Browser:** http://localhost:3000

2. **Test Text Search:**
   - Type a query: "black sneakers" or "summer dress"
   - Click "Search"
   - Should see results with match scores

3. **Test Image Search:**
   - Click "Image Search" tab
   - Upload an image file
   - Click "Search Similar Products"
   - Should see visually similar products

4. **Test Explore Feed:**
   - Click "Explore Feed" tab
   - Should see scraped images (if any)
   - Click on an image to search similar products

5. **Test Product Details:**
   - Click on any product in results
   - Should open modal with product details
   - Check all information displays correctly

### ✅ Step 4: Test Database

```powershell
python tests/test_database.py
```

This will verify:
- Database connection
- pgvector extension
- Tables exist
- Products have embeddings
- Metadata extracted

### ✅ Step 5: Test API Endpoints

```powershell
# Make sure backend is running first
python tests/test_api.py
```

This will test:
- Health endpoint
- Text search
- Image search
- Response times

## Expected Results

### Backend Should Show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Should Show:
```
  ▲ Next.js 14.2.33
  - Local:        http://localhost:3000
  - Ready in Xs
```

### Browser Should Show:
- Vibe Search homepage
- Search interface (text + image)
- Results grid (after search)
- Explore feed tab

## Troubleshooting

### Backend Won't Start

**Error: "Port 8000 already in use"**
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Error: "Module not found"**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Won't Start

**Error: "Port 3000 already in use"**
```powershell
# Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Error: "Cannot find module"**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### Frontend Can't Connect to Backend

1. Check backend is running: http://localhost:8000/docs
2. Check CORS settings in `api/main.py`
3. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`

### No Search Results

1. Check database has products: `python tests/test_database.py`
2. Check embeddings are generated
3. Check backend logs for errors
4. Check browser console (F12) for API errors

## Complete Test Flow

1. **Start Everything:**
   ```powershell
   .\start_all.ps1
   ```

2. **Wait for Both Servers:**
   - Backend: "Uvicorn running"
   - Frontend: "Ready"

3. **Test in Browser:**
   - Open http://localhost:3000
   - Try text search
   - Try image upload
   - Check explore feed
   - View product details

4. **Test API Directly:**
   - Visit http://localhost:8000/docs
   - Try all endpoints
   - Check response times

5. **Run Test Suites:**
   ```powershell
   python tests/test_database.py
   python tests/test_api.py
   ```

## Performance Checks

- **API Response Time:** Should be < 500ms
- **Frontend Load Time:** Should be < 3 seconds
- **Search Results:** Should appear within 1-2 seconds

## Success Criteria

✅ Backend starts without errors
✅ Frontend starts without errors
✅ Can access both in browser
✅ Text search returns results
✅ Image search returns results
✅ Product details display correctly
✅ All test suites pass
✅ Response times are acceptable

## Next Steps After Testing

1. **Record Demo Video:**
   - Show all features
   - Keep under 5 minutes
   - Highlight key capabilities

2. **Fix Any Issues:**
   - Note any errors
   - Fix bugs
   - Re-test

3. **Deploy/Share:**
   - Upload to GitHub
   - Or deploy to cloud
   - Share with others

Your project is ready to test! 🚀

