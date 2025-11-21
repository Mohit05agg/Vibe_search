"""
Complete processing pipeline for scraped images.
Downloads -> Detects -> Filters -> Crops -> Embeds -> Extracts Metadata
"""

import logging
import os
import io
import hashlib
from typing import Dict, Optional, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

from ai.object_detector import ObjectDetector
from ai.clip_embedding import ClipEmbeddingExtractor
from ai.quality_filter import QualityFilter
from ai.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ImageProcessingPipeline:
    """
    Orchestrates image processing and returns structured records.
    Each processed image returns a dict like:
    {
      "detections": {"primary": {...}, "all": [...]},
      "embedding": [...],
      "colors": [...],
      "styles": [...],
      "brands": [...],
      "quality": {...},
      "local_path": "...",
      "image_url": "..."
    }
    """

    def __init__(self, download_dir: Optional[str] = None, max_workers: int = 4, save_local: bool = True, min_confidence: float = 0.35, min_crop_area: int = 64 * 64):
        self.download_dir = Path(download_dir) if download_dir else None
        self.max_workers = max_workers
        self.save_local = save_local
        self.min_confidence = float(min_confidence)
        self.min_crop_area = int(min_crop_area)

        self.object_detector: Optional[ObjectDetector] = None
        self.embedding_extractor: Optional[ClipEmbeddingExtractor] = None
        self.quality_filter: Optional[QualityFilter] = None
        self.metadata_extractor: Optional[MetadataExtractor] = None

        if self.download_dir and self.save_local:
            self.download_dir.mkdir(parents=True, exist_ok=True)

    def _init_components(self):
        if self.object_detector is None:
            try:
                self.object_detector = ObjectDetector()
            except Exception as e:
                logger.warning(f"ObjectDetector init failed: {e}")
                self.object_detector = None
        if self.embedding_extractor is None:
            try:
                self.embedding_extractor = ClipEmbeddingExtractor()
            except Exception as e:
                logger.warning(f"ClipEmbeddingExtractor init failed: {e}")
                self.embedding_extractor = None
        if self.quality_filter is None:
            self.quality_filter = QualityFilter()
        if self.metadata_extractor is None:
            self.metadata_extractor = MetadataExtractor()

    def _download_image(self, url: str, timeout: int = 5, max_retries: int = 2) -> Optional[Image.Image]:
        if not url:
            return None
        headers = {'User-Agent': 'Mozilla/5.0'}
        for attempt in range(max_retries):
            try:
                r = requests.get(url, headers=headers, timeout=timeout)
                r.raise_for_status()
                content_type = r.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    logger.debug(f"Not an image content-type: {content_type} for {url}")
                    return None
                img = Image.open(io.BytesIO(r.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return img
            except Exception as e:
                logger.debug(f"Download attempt {attempt+1} failed for {url}: {e}")
                continue
        logger.warning(f"Failed to download image after retries: {url}")
        return None

    def _save_local(self, img: Image.Image, image_url: str, suffix: str = "orig") -> Optional[str]:
        if not self.save_local or not self.download_dir:
            return None
        try:
            name = hashlib.md5(image_url.encode("utf-8")).hexdigest()[:12]
            filename = f"{name}_{suffix}.jpg"
            path = self.download_dir / filename
            img.save(path, format='JPEG', quality=85)
            return str(path)
        except Exception as e:
            logger.debug(f"Failed to save local image: {e}")
            return None

    def process_image(self, image_url: str, caption: Optional[str] = None, source: str = "unknown", source_url: Optional[str] = None) -> Optional[Dict]:
        """
        Process a single image. Returns structured dict or None.
        """
        self._init_components()
        try:
            image = self._download_image(image_url)
            if image is None:
                logger.debug(f"Image download failed: {image_url}")
                return None

            local_orig = self._save_local(image, image_url, "orig")

            # Quality check on original
            q = self.quality_filter.check_image(image, return_details=True)
            is_safe = q.get('is_safe', False)
            quality_details = q.get('details', {})

            if not is_safe:
                logger.debug(f"Image rejected by quality filter: {image_url}")
                return {"image_url": image_url, "local_path": local_orig, "quality": quality_details, "detections": {"primary": None, "all": []}, "embedding": None, "colors": [], "styles": [], "brands": []}

            # Object detection
            detections_list = []
            primary = None
            if self.object_detector:
                try:
                    detections_list = self.object_detector.detect(image, return_crops=True) or []
                    # Get primary (most confident) detection
                    if detections_list:
                        primary = max(detections_list, key=lambda x: x.get('confidence', 0.0))
                except Exception as e:
                    logger.debug(f"Object detection failed for {image_url}: {e}")
                    detections_list = []
                    primary = None

            # Format detections for response
            detections = {
                "primary": primary,
                "all": detections_list
            }

            # If there is a primary detection use its crop for embedding, else use full image
            if primary and primary.get('crop'):
                crop_for_embedding = primary.get('crop')
            else:
                crop_for_embedding = image

            # Embedding (prefer batch if multiple crops later)
            embedding = None
            if self.embedding_extractor:
                try:
                    embedding = self.embedding_extractor.extract_embedding(crop_for_embedding)
                except Exception as e:
                    logger.debug(f"Embedding failed for {image_url}: {e}")
                    embedding = None

            # Metadata extraction (prefer crop for colors)
            try:
                meta_source_img = crop_for_embedding if crop_for_embedding else image
                metadata = self.metadata_extractor.extract_all(image=meta_source_img, text=caption)
            except Exception as e:
                logger.debug(f"Metadata extraction failed for {image_url}: {e}")
                metadata = {"colors": [], "styles": [], "brands": []}

            result = {
                "image_url": image_url,
                "source_url": source_url,
                "local_path": local_orig,
                "detections": detections,
                "embedding": embedding,
                "colors": metadata.get("colors", []),
                "styles": metadata.get("styles", []),
                "brands": metadata.get("brands", []),
                "quality": quality_details
            }
            return result
        except Exception as e:
            logger.exception(f"Unexpected error in process_image: {e}")
            return None

    def process_images_batch(self, image_data_list: List[Dict], source: str = "unknown") -> List[Dict]:
        """
        Process multiple images in parallel and return list of result dicts.
        """
        results: List[Dict] = []
        if not image_data_list:
            return results

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(self.process_image, item.get("image_url"), item.get("caption"), item.get("source", source), item.get("source_url")): item
                for item in image_data_list
            }
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    res = future.result()
                    if res:
                        results.append(res)
                except Exception as e:
                    logger.exception(f"Batch processing error for {item.get('image_url')}: {e}")
        return results
