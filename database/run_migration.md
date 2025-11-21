# How to Run Database Migration

## Step 1: Open WSL Terminal

1. Press `Win + X` and select "Terminal" or "Windows PowerShell"
2. Type: `wsl` or `ubuntu`
3. Press Enter

You should now be in a WSL bash terminal (you'll see a prompt like `username@computer:~$`)

## Step 2: Navigate to Project Directory

```bash
# Navigate to your project (adjust path if different)
cd /mnt/d/CultureCircleTask/database
```

Or if you're already in the project root:
```bash
cd database
```

## Step 3: Make Sure PostgreSQL is Running

```bash
# Start PostgreSQL if not running
sudo service postgresql start

# Verify it's running
sudo service postgresql status
```

You should see: `Active: active (running)`

## Step 4: Run the Migration

**Option A: Using psql with file (Recommended)**

```bash
# Set password if needed (replace 'postgres' with your actual password)
export PGPASSWORD='postgres'

# Run the migration
psql -U postgres -d vibe_search -f schema_update_scraped_images.sql
```

**Option B: Using sudo (if password doesn't work)**

```bash
sudo -u postgres psql -d vibe_search -f schema_update_scraped_images.sql
```

**Option C: Interactive psql**

```bash
# Connect to database
sudo -u postgres psql -d vibe_search

# Then copy and paste the SQL from schema_update_scraped_images.sql
# Or run:
\i schema_update_scraped_images.sql

# Exit when done
\q
```

## Step 5: Verify Migration Success

```bash
# Connect to database
sudo -u postgres psql -d vibe_search

# Check if new columns exist
\d scraped_images

# You should see the new columns:
# - detected_class
# - bbox
# - extracted_colors
# - extracted_styles
# - extracted_brands
# - local_path
# - quality_score

# Exit
\q
```

## Alternative: Run from Windows PowerShell

If you have `psql` installed on Windows (via PostgreSQL installer), you can also run:

```powershell
# Make sure PostgreSQL is running in WSL first
wsl sudo service postgresql start

# Then run (adjust path)
psql -U postgres -d vibe_search -h localhost -f D:\CultureCircleTask\database\schema_update_scraped_images.sql
```

## Troubleshooting

### "psql: command not found"
- PostgreSQL client tools not installed
- Install: `sudo apt install postgresql-client`

### "password authentication failed"
- Set password: `export PGPASSWORD='your_password'`
- Or use: `sudo -u postgres psql` (no password needed)

### "database does not exist"
- Create it first:
  ```bash
  sudo -u postgres psql
  CREATE DATABASE vibe_search;
  CREATE EXTENSION vector;
  \q
  ```

### "permission denied"
- Use `sudo` before the command
- Or make sure you're using the postgres user

## Expected Output

You should see messages like:
```
ALTER TABLE
ALTER TABLE
CREATE INDEX
CREATE INDEX
...
```

No errors means the migration was successful! ✅

