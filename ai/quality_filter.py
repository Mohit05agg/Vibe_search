"""
Quality filtering for images.
Includes NSFW detection and blur detection.
"""

import logging
from typing import Dict, Optional, Tuple
import io

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False
    logger.warning("opencv-python not installed. Blur detection disabled.")

try:
    from nudenet import NudeClassifier
    NUDENET_AVAILABLE = True
except Exception:
    NUDENET_AVAILABLE = False
    logger.warning("nudenet not installed. NSFW detection disabled.")


class QualityFilter:
    """
    Quality filter for images.
    """

    def __init__(
        self,
        nsfw_threshold: float = 0.6,
        blur_threshold: float = 50.0,
        min_size: Tuple[int, int] = (100, 100)
    ):
        self.nsfw_threshold = float(nsfw_threshold)
        self.blur_threshold = float(blur_threshold)
        self.min_size = tuple(min_size)
        self.nsfw_classifier = None
        if NUDENET_AVAILABLE:
            try:
                # Use classifier (NudeClassifier returns probabilities for safe/unsafe classes)
                self.nsfw_classifier = NudeClassifier()
            except Exception as e:
                logger.warning(f"Could not initialize NudeClassifier: {e}")
                self.nsfw_classifier = None

    def _detect_blur(self, image: Image.Image) -> float:
        """
        Return Laplacian variance (higher = sharper).
        """
        if not CV2_AVAILABLE:
            return 100.0  # best-effort default

        try:
            arr = np.array(image.convert('L'))
            lap = cv2.Laplacian(arr, cv2.CV_64F).var()
            return float(lap)
        except Exception as e:
            logger.debug(f"Blur detection failed: {e}")
            return 0.0

    def _detect_nsfw(self, image: Image.Image) -> float:
        """
        Return NSFW score between 0..1 (higher = more NSFW).
        """
        if not self.nsfw_classifier:
            return 0.0
        try:
            buf = io.BytesIO()
            image.save(buf, format='JPEG')
            buf.seek(0)
            # classifier.classify returns dict-like mapping; adapt accordingly
            out = self.nsfw_classifier.classify(buf.getvalue())
            # find max NSFW prob if present
            max_score = 0.0
            if isinstance(out, dict):
                for _, v in out.items():
                    if isinstance(v, dict):
                        # search nested probabilities
                        for _, p in v.items():
                            try:
                                max_score = max(max_score, float(p))
                            except Exception:
                                continue
            return float(max_score)
        except Exception as e:
            logger.debug(f"NSFW detection failed: {e}")
            return 0.0

    def check_image(self, image: Image.Image, return_details: bool = False) -> Dict:
        """
        Check image quality and returns structured dict.
        """
        try:
            width, height = image.size
            is_valid_size = (width >= self.min_size[0] and height >= self.min_size[1])
            blur_score = self._detect_blur(image)
            is_blurry = blur_score < self.blur_threshold
            nsfw_score = self._detect_nsfw(image)
            is_nsfw = nsfw_score > self.nsfw_threshold

            final_safe = is_valid_size and (not is_blurry) and (not is_nsfw)

            details = {
                "width": width,
                "height": height,
                "aspect_ratio": width / max(height, 1),
                "blur_score": blur_score,
                "nsfw_score": nsfw_score,
                "is_blurry": is_blurry,
                "is_nsfw": is_nsfw,
                "is_valid_size": is_valid_size
            }

            if return_details:
                return {"is_safe": final_safe, "details": details}
            return {"is_safe": final_safe}
        except Exception as e:
            logger.exception(f"Quality check failed: {e}")
            return {"is_safe": False, "details": {}}

    # backward compatibility
    def filter_image(self, image):
        out = self.check_image(image, return_details=True)
        return out.get("is_safe", False), out.get("details", {})
