"""
Health check endpoints.
"""

from fastapi import APIRouter, HTTPException
from api.database import get_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

