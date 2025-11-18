# Frontend Troubleshooting Guide

## Check if Frontend is Running

### Method 1: Check Port
```powershell
netstat -ano | findstr :3000
```
If you see output, the server is running. If not, it's not running.

### Method 2: Try Accessing
Open your browser and go to: `http://localhost:3000`

## Common Issues and Solutions

### Issue 1: "Port 3000 is already in use"

**Solution:**
```powershell
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F

# Or use a different port
cd frontend
$env:PORT=3001; npm run dev
```

### Issue 2: "Cannot find module" or Import Errors

**Solution:**
```powershell
cd frontend
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

### Issue 3: "TypeScript Errors"

**Solution:**
```powershell
cd frontend
# Check for TypeScript errors
npm run build

# Or fix linting issues
npm run lint
```

### Issue 4: Frontend Loads but Shows Errors

**Check:**
1. Is the backend API running? (`python run_server.py`)
2. Check browser console (F12) for errors
3. Check if API_URL is correct in `.env.local`

### Issue 5: "Module not found" Errors

**Solution:**
```powershell
cd frontend
# Reinstall dependencies
npm install

# Clear Next.js cache
Remove-Item -Recurse -Force .next
npm run dev
```

## Step-by-Step Startup

### 1. Start Backend First
```powershell
# In Terminal 1
cd D:\CultureCircleTask
python run_server.py
```
Wait for: "Uvicorn running on http://0.0.0.0:8000"

### 2. Start Frontend
```powershell
# In Terminal 2
cd D:\CultureCircleTask\frontend
npm run dev
```
Wait for: "Ready - started server on 0.0.0.0:3000"

### 3. Open Browser
Go to: `http://localhost:3000`

## Verify Everything is Working

### Check Backend
- Visit: `http://localhost:8000/docs`
- Should show FastAPI documentation

### Check Frontend
- Visit: `http://localhost:3000`
- Should show Vibe Search homepage

### Check Connection
- Open browser DevTools (F12)
- Go to Network tab
- Try a search
- Check if API calls are successful

## Environment Variables

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Error Messages

### "ECONNREFUSED"
- Backend is not running
- Start backend: `python run_server.py`

### "404 Not Found"
- API endpoint doesn't exist
- Check API routes in `api/routers/`

### "CORS error"
- Backend CORS not configured
- Check `api/main.py` CORS settings

### "Module not found: Can't resolve"
- Missing dependency
- Run: `cd frontend && npm install`

## Quick Fixes

### Reset Everything
```powershell
# Stop all servers (Ctrl+C)

# Frontend
cd frontend
Remove-Item -Recurse -Force node_modules .next
npm install
npm run dev

# Backend (in another terminal)
cd D:\CultureCircleTask
python run_server.py
```

### Check Logs
- Frontend logs: Check the terminal where `npm run dev` is running
- Backend logs: Check the terminal where `python run_server.py` is running
- Browser console: Press F12 in browser

## Still Not Working?

1. **Check Node.js version:**
   ```powershell
   node --version
   ```
   Should be 18+ (you have 24.11.1 ✓)

2. **Check if files exist:**
   ```powershell
   Test-Path frontend\app\page.tsx
   Test-Path frontend\components\SearchInterface.tsx
   ```

3. **Check for syntax errors:**
   ```powershell
   cd frontend
   npm run build
   ```

4. **Check port availability:**
   ```powershell
   netstat -ano | findstr ":3000 :8000"
   ```

