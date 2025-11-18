# Start PostgreSQL Database

The backend needs PostgreSQL to be running. Since you're using WSL, follow these steps:

## Start PostgreSQL in WSL

### Step 1: Open WSL Terminal

1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"
3. Type: `wsl` or `ubuntu`
4. Press Enter

### Step 2: Start PostgreSQL

```bash
# Start PostgreSQL service
sudo service postgresql start

# Verify it's running
sudo service postgresql status
```

You should see: `Active: active (running)`

### Step 3: Verify Database Exists

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In psql, check database
\l

# You should see 'vibe_search' in the list
# If not, create it:
CREATE DATABASE vibe_search;
\c vibe_search
CREATE EXTENSION vector;
\q
```

### Step 4: Test Connection from Windows

After starting PostgreSQL in WSL, test from Windows:

```powershell
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='vibe_search', user='postgres', password='postgres'); print('Database connected!'); conn.close()"
```

## Quick Start Command

Once in WSL terminal, just run:
```bash
sudo service postgresql start
```

## Verify Everything

After starting PostgreSQL, run the test again:

```powershell
python test_full_project.py
```

All tests should pass once the database is running!

## Troubleshooting

### "Service not found"
- PostgreSQL might not be installed in WSL
- Install: `sudo apt install postgresql-18`

### "Permission denied"
- Use `sudo` before the command

### "Connection refused" from Windows
- Make sure PostgreSQL is configured to accept connections
- Check `/etc/postgresql/18/main/postgresql.conf` has `listen_addresses = 'localhost'`
- Check `/etc/postgresql/18/main/pg_hba.conf` allows connections

