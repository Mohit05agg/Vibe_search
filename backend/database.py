"""Database connection utilities."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Create database connection with dict cursor."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        cursor_factory=RealDictCursor
    )

