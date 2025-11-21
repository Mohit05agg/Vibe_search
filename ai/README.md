# AI Processing Modules

This directory contains AI-powered processing modules for scraped images, providing object detection, embedding generation, quality filtering, and metadata extraction.

## Modules

### 1. `object_detector.py` - Object Detection
- **Purpose**: Detects fashion items in images using YOLOv8/YOLOv11
- **Features**:
  - Detects objects with bounding boxes
  - Maps detections to fashion categories (shirt, pants, shoes, etc.)
  - Returns cropped images of detected objects
- **Dependencies**: `ultralytics` (YOLOv8/YOLOv11)

### 2. `clip_embedding.py` - CLIP Embeddings
- **Purpose**: Generates 512-dimensional CLIP embeddings for visual search
- **Features**:
  - Image embedding extraction
  - Text embedding extraction
  - Batch processing support
  - Normalized embeddings for cosine similarity
- **Dependencies**: `transformers`, `torch`

### 3. `quality_filter.py` - Quality Filtering
- **Purpose**: Filters images based on quality and content safety
- **Features**:
  - NSFW content detection (using NudeNet)
  - Blur detection (using Laplacian variance)
  - Minimum size validation
  - Returns quality scores
- **Dependencies**: `opencv-python`, `nudenet`

### 4. `metadata_extractor.py` - Metadata Extraction
- **Purpose**: Extracts colors, styles, and brands from images and text
- **Features**:
  - Color extraction from images (dominant colors)
  - Style keyword extraction from text
  - Brand name extraction from text
  - Combines image and text analysis
- **Dependencies**: `PIL`, `numpy`, existing `metadata.extract_metadata` module

### 5. `processing_pipeline.py` - Complete Pipeline
- **Purpose**: Orchestrates the complete processing workflow
- **Workflow**:
  1. Download image from URL
  2. Quality filter (NSFW, blur, size)
  3. Object detection
  4. Crop detected objects
  5. Generate CLIP embeddings
  6. Extract metadata (colors, styles, brands)
  7. Return structured JSON result
- **Features**:
  - Parallel processing support
  - Local image saving (optional)
  - Error handling and retries
  - Structured output format

## Usage

### Basic Usage

```python
from ai.processing_pipeline import ImageProcessingPipeline

# Initialize pipeline
pipeline = ImageProcessingPipeline(
    download_dir="./downloads",  # Optional: save images locally
    max_workers=4,  # Parallel processing
    save_local=True
)

# Process a single image
result = pipeline.process_image(
    image_url="https://example.com/image.jpg",
    caption="Nike Air Max sneakers",
    source="pinterest",
    source_url="https://pinterest.com/pin/123"
)

# Result structure:
# {
#     'source': 'pinterest',
#     'image_url': '...',
#     'local_path': '...',
#     'detected_class': 'shoes',
#     'bbox': [x1, y1, x2, y2],
#     'embedding': [0.1, 0.2, ...],  # 512-dim vector
#     'colors': ['black', 'white'],
#     'styles': ['sporty', 'athletic'],
#     'brands': ['Nike'],
#     'quality_score': {'blur_score': 150.5, 'nsfw_score': 0.0}
# }
```

### Using Individual Modules

```python
from ai.object_detector import ObjectDetector
from ai.clip_embedding import ClipEmbeddingExtractor
from ai.quality_filter import QualityFilter
from ai.metadata_extractor import MetadataExtractor
from PIL import Image

# Object detection
detector = ObjectDetector()
image = Image.open("image.jpg")
detections = detector.detect(image, return_crops=True)

# CLIP embeddings
embedder = ClipEmbeddingExtractor()
embedding = embedder.extract_embedding(image)

# Quality filtering
filter = QualityFilter()
is_safe, result = filter.filter_image(image)

# Metadata extraction
extractor = MetadataExtractor()
metadata = extractor.extract_all(
    image=image,
    text="Nike Air Max sneakers",
    existing_brand="Nike"
)
```

## Integration with Scrapers

The scrapers (`pinterest_scraper.py`, `instagram_scraper.py`) automatically use the AI processing pipeline when `enable_ai_processing=True`:

```python
from scrapers.pinterest_scraper import PinterestScraper

with PinterestScraper(
    enable_ai_processing=True,
    download_dir="./downloads"
) as scraper:
    results = scraper.scrape("https://pinterest.com/board/...", limit=50)
    # Results include AI-processed data
```

## Installation

Install required dependencies:

```bash
pip install ultralytics opencv-python nudenet
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

## Output Format

The processing pipeline returns structured JSON with the following format:

```json
{
    "source": "pinterest",
    "image_url": "https://...",
    "local_path": "./downloads/pinterest_123456.jpg",
    "detected_class": "shirt",
    "bbox": [100, 150, 300, 400],
    "confidence": 0.85,
    "embedding": [0.1, 0.2, 0.3, ...],  // 512 dimensions
    "colors": ["black", "white"],
    "styles": ["casual", "streetwear"],
    "brands": ["Nike"],
    "quality_score": {
        "blur_score": 150.5,
        "nsfw_score": 0.0
    }
}
```

## Performance

- **Object Detection**: ~100-200ms per image (GPU), ~500-1000ms (CPU)
- **CLIP Embedding**: ~50-100ms per image (GPU), ~200-500ms (CPU)
- **Quality Filter**: ~20-50ms per image
- **Metadata Extraction**: ~10-30ms per image
- **Total Pipeline**: ~200-400ms per image (GPU), ~800-1500ms (CPU)

With parallel processing (4 workers), throughput is approximately 4x faster.

## Notes

- Models are loaded lazily (on first use) to optimize startup time
- GPU acceleration is automatically used if available
- Failed processing steps fall back gracefully (basic data saved without AI processing)
- NSFW and blur detection can be disabled if dependencies are not installed

