"""
FastAPI backend for Vibe Search.
Main application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import search, health, feed

app = FastAPI(
    title="Vibe Search API",
    description="Multimodal search engine for fashion and lifestyle products",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(feed.router, prefix="/api", tags=["feed"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Vibe Search API",
        "version": "1.0.0",
        "docs": "/docs"
    }

