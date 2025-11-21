"""
Metadata extraction from images and text.
Extracts colors, styles, and brands using simple image analysis and NLP hooks.
"""

import logging
import re
from typing import List, Optional, Dict
from collections import Counter

from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Minimal color map - you can expand or load from a JSON file
COLOR_RGB_MAP = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 128, 0),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'brown': (165, 42, 42),
    'gray': (128, 128, 128),
    'beige': (245, 245, 220),
    'navy': (0, 0, 128)
}

# simple style keywords for text matching - extend as needed
STYLE_KEYWORDS = ['streetwear', 'minimal', 'luxury', 'casual', 'vintage', 'formal', 'sporty', 'ethnic']

def _closest_color_name(r: int, g: int, b: int) -> Optional[str]:
    """Return closest color name from COLOR_RGB_MAP (int inputs)."""
    try:
        # Clamp values to valid range to avoid overflow
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        
        min_dist = float('inf')
        best = None
        for name, (cr, cg, cb) in COLOR_RGB_MAP.items():
            dr = r - cr
            dg = g - cg
            db = b - cb
            dist = (dr * dr) + (dg * dg) + (db * db)
            if dist < min_dist:
                min_dist = dist
                best = name
        # threshold to avoid weird matches
        if min_dist < (100 * 100):
            return best.title() if best else None
        return None
    except Exception:
        return None


class MetadataExtractor:
    """
    Metadata extractor for images and text.
    """

    def __init__(self, top_k_colors: int = 3):
        self.top_k_colors = int(top_k_colors)

    def extract_all(self, image: Optional[Image.Image] = None, text: Optional[str] = None, existing_brand: Optional[str] = None) -> Dict:
        """
        Returns: {'colors': [...], 'styles': [...], 'brands': [...]}
        """
        result = {'colors': [], 'styles': [], 'brands': []}
        try:
            # Text extraction (brands, styles, colors)
            if text:
                text_lower = text.lower()
                # styles
                styles = [kw for kw in STYLE_KEYWORDS if kw in text_lower]
                result['styles'].extend(styles)
                # brands heuristics: simple regex for capitalized words - you can replace with LLM
                brand_matches = re.findall(r'\b([A-Z][a-zA-Z0-9&]+)\b', text)
                if existing_brand:
                    brand_matches.append(existing_brand)
                result['brands'].extend([b for b in brand_matches if len(b) > 1])

            # Image color extraction
            if image:
                try:
                    img = image.copy()
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    arr = np.array(img)
                    # reshape and quantize
                    pixels = arr.reshape(-1, 3)
                    # convert to ints to avoid uint8 underflow/overflow
                    pixels = pixels.astype(int)
                    # simple quantization by rounding
                    quant = (pixels // 32) * 32
                    counts = Counter([tuple(p) for p in quant])
                    top = counts.most_common(self.top_k_colors)
                    for (r, g, b), _ in top:
                        name = _closest_color_name(int(r), int(g), int(b))
                        if name:
                            result['colors'].append(name)
                except Exception as e:
                    logger.debug(f"Image color extraction failed: {e}")

            # dedupe & normalize
            result['colors'] = list(dict.fromkeys([c.title() for c in result.get('colors', [])]))
            result['styles'] = list(dict.fromkeys([s.lower() for s in result.get('styles', [])]))
            result['brands'] = list(dict.fromkeys([b.strip() for b in result.get('brands', []) if b.strip()]))

            return result
        except Exception as e:
            logger.exception(f"Metadata extraction failed: {e}")
            return {'colors': [], 'styles': [], 'brands': []}
