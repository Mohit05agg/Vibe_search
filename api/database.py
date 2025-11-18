"""
Database connection utilities.
"""

import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "vibe_search"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def get_db_cursor(conn=None):
    """Get database cursor with RealDictCursor for easier dict access."""
    if conn is None:
        conn = get_db_connection()
    return conn.cursor(cursor_factory=RealDictCursor)

