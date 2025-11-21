-- ==========================================
-- AI-Enhanced Migration for scraped_images
-- ==========================================

-- 1. Drop old unique constraint (in case it exists)
ALTER TABLE scraped_images 
    DROP CONSTRAINT IF EXISTS scraped_images_source_url_key;

-- 2. Add new unique constraint (source + image_url)
ALTER TABLE scraped_images 
    ADD CONSTRAINT scraped_images_source_image_url_key UNIQUE (source, image_url);


-- ==========================================
-- Add Columns for AI Processing
-- ==========================================

-- YOLO object detection
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS detected_class VARCHAR(100);
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS bbox INTEGER[];  -- [x1, y1, x2, y2]

-- CLIP embedding (vector(512))
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS image_embedding vector(512);

-- Color extraction
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS extracted_colors TEXT[];

-- Style tags from metadata extractor
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS extracted_styles TEXT[];

-- Brand detection
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS extracted_brands TEXT[];

-- Local disk storage path
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS local_path TEXT;

-- Image quality metrics
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS quality_score JSONB;

-- Large language model metadata (optional)
ALTER TABLE scraped_images ADD COLUMN IF NOT EXISTS metadata JSONB;




-- ==========================================
-- PERFORMANCE INDEXES
-- ==========================================

-- Fast filtering by class
CREATE INDEX IF NOT EXISTS idx_scraped_images_detected_class 
    ON scraped_images (detected_class);

-- Fast searching for colors/styles/brands
CREATE INDEX IF NOT EXISTS idx_scraped_images_extracted_colors 
    ON scraped_images USING GIN (extracted_colors);

CREATE INDEX IF NOT EXISTS idx_scraped_images_extracted_styles 
    ON scraped_images USING GIN (extracted_styles);

CREATE INDEX IF NOT EXISTS idx_scraped_images_extracted_brands 
    ON scraped_images USING GIN (extracted_brands);

-- Fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_scraped_images_embedding_hnsw
    ON scraped_images USING hnsw (image_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Fast metadata querying
CREATE INDEX IF NOT EXISTS idx_scraped_images_metadata_gin
    ON scraped_images USING GIN (metadata);

