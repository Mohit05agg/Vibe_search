# How to Start the Complete Project

## Quick Start - All at Once

### Option 1: Use Start Script
```powershell
.\start_all.ps1
```

### Option 2: Manual Start (3 Terminals)

## Required Services

You need **3 things** running:

1. **PostgreSQL Database** (in WSL)
2. **Backend API** (Python/FastAPI)
3. **Frontend** (Next.js)

## Step-by-Step Startup

### Step 1: Start PostgreSQL (WSL Terminal)

```bash
# In WSL terminal
sudo service postgresql start

# Verify it's running
sudo service postgresql status
```

### Step 2: Start Backend (PowerShell Terminal 1)

```powershell
cd D:\CultureCircleTask
python run_server.py
```

**Wait for:** `Uvicorn running on http://0.0.0.0:8000`

### Step 3: Start Frontend (PowerShell Terminal 2)

```powershell
cd D:\CultureCircleTask\frontend
npm run dev
```

**Wait for:** `Ready - started server on 0.0.0.0:3000`

## Verify Everything is Running

### Check Backend
- Visit: http://localhost:8000/docs
- Should show API documentation

### Check Frontend
- Visit: http://localhost:3000
- Should show Vibe Search homepage

### Check Database
```powershell
python tests/test_database.py
```

## Test the Complete Project

Once all 3 are running:

```powershell
python test_full_project.py
```

This will test:
- ✅ Backend health
- ✅ Frontend accessibility
- ✅ Database connection
- ✅ API endpoints
- ✅ Text search
- ✅ Image search
- ✅ Performance

## Current Status

Based on the test:
- ✅ Frontend: Running on port 3000
- ❌ Backend: Not running (needs to be started)
- ❌ Database: Not accessible (needs PostgreSQL in WSL)

## Next Steps

1. **Start PostgreSQL in WSL:**
   ```bash
   sudo service postgresql start
   ```

2. **Start Backend:**
   ```powershell
   python run_server.py
   ```

3. **Test Again:**
   ```powershell
   python test_full_project.py
   ```

4. **Open Browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## Troubleshooting

### Backend Won't Start

**Error: "Module not found"**
```powershell
pip install -r requirements.txt
```

**Error: "Port 8000 in use"**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Failed

**PostgreSQL not running in WSL:**
```bash
# In WSL
sudo service postgresql start
```

**Connection refused:**
- Check PostgreSQL is configured to accept connections from Windows
- See `COMPLETE_SETUP.md` for database configuration

### Frontend Can't Connect to Backend

1. Make sure backend is running
2. Check CORS in `api/main.py`
3. Check `NEXT_PUBLIC_API_URL` in frontend

## All Services Running Checklist

- [ ] PostgreSQL running in WSL
- [ ] Backend API running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:3000
- [ ] Test suite passes

Once all checked, your project is fully operational! 🚀

