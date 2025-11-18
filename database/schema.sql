-- Vibe Search Database Schema
-- PostgreSQL 18 with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Products table with all CSV fields plus vector embeddings
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    sku_id VARCHAR(100),
    title TEXT NOT NULL,
    slug VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    brand_name VARCHAR(100),
    product_type VARCHAR(100),
    gender VARCHAR(20),
    colorways TEXT,
    brand_sku VARCHAR(100),
    model VARCHAR(100),
    lowest_price DECIMAL(10, 2),
    description TEXT,
    is_d2c BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_certificate_required BOOLEAN DEFAULT FALSE,
    featured_image TEXT,
    quantity_left INTEGER,
    wishlist_num INTEGER,
    stock_claimed_percent INTEGER,
    discount_percentage DECIMAL(5, 2),
    note TEXT,
    tags TEXT,
    release_date DATE,
    pdp_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Extracted metadata columns
    extracted_colors TEXT[],  -- Array of extracted colors
    extracted_styles TEXT[],   -- Array of extracted styles
    extracted_brands TEXT[],   -- Array of extracted brands (if multiple)
    
    -- Vector embeddings
    image_embedding vector(512),  -- CLIP embedding for visual search
    text_embedding vector(384),   -- Sentence transformer embedding for text search
    
    -- Indexes for performance
    CONSTRAINT products_product_id_key UNIQUE (product_id)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand_name ON products(brand_name);
CREATE INDEX IF NOT EXISTS idx_products_gender ON products(gender);
CREATE INDEX IF NOT EXISTS idx_products_lowest_price ON products(lowest_price);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Vector similarity indexes (HNSW for fast approximate nearest neighbor search)
CREATE INDEX IF NOT EXISTS idx_products_image_embedding ON products 
    USING hnsw (image_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_products_text_embedding ON products 
    USING hnsw (text_embedding vector_cosine_ops);

-- Scraped images table for Pinterest/Instagram feed
CREATE TABLE IF NOT EXISTS scraped_images (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'pinterest' or 'instagram'
    source_url TEXT NOT NULL,
    image_url TEXT NOT NULL,
    caption TEXT,
    hashtags TEXT[],
    engagement_count INTEGER DEFAULT 0,
    username VARCHAR(255),
    board_name VARCHAR(255),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_embedding vector(512),  -- CLIP embedding for click-to-search
    CONSTRAINT scraped_images_source_url_key UNIQUE (source_url)
);

CREATE INDEX IF NOT EXISTS idx_scraped_images_source ON scraped_images(source);
CREATE INDEX IF NOT EXISTS idx_scraped_images_scraped_at ON scraped_images(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_scraped_images_embedding ON scraped_images 
    USING hnsw (image_embedding vector_cosine_ops);

