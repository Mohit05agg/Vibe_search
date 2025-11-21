"""
AI processing modules for scraped images.
Includes object detection, embedding generation, quality filtering, and metadata extraction.
"""

from ai.object_detector import ObjectDetector
from ai.clip_embedding import ClipEmbeddingExtractor
from ai.quality_filter import QualityFilter
from ai.metadata_extractor import MetadataExtractor

__all__ = [
    'ObjectDetector',
    'ClipEmbeddingExtractor',
    'QualityFilter',
    'MetadataExtractor'
]

