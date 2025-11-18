"""
Setup database schema by executing SQL file.
"""

import os
import psycopg2
from pathlib import Path


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def setup_schema():
    """Execute schema.sql to create tables."""
    schema_file = Path(__file__).parent / "schema.sql"
    
    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print(f"Reading schema from {schema_file}")
        with schema_file.open('r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema (split by semicolons, but handle CREATE EXTENSION separately)
        # Remove CREATE EXTENSION IF NOT EXISTS vector; as it should already exist
        schema_sql = schema_sql.replace('CREATE EXTENSION IF NOT EXISTS vector;', '')
        
        print("Executing schema...")
        cursor.execute(schema_sql)
        conn.commit()
        
        print("Schema created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[t[0] for t in tables]}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error setting up schema: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("Setting up database schema...")
    print("-" * 50)
    success = setup_schema()
    if success:
        print("\nDatabase setup complete!")
    else:
        print("\nDatabase setup failed!")
        exit(1)

