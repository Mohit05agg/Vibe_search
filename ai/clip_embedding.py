"""
CLIP embedding extraction for images and text.
Generates embeddings for visual search.
"""

import logging
from typing import List, Optional
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ClipEmbeddingExtractor:
    """
    CLIP embedding extractor for images and cropped objects.
    """

    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model: Optional[CLIPModel] = None
        self.processor: Optional[CLIPProcessor] = None

        self._load_model()

    def _load_model(self):
        """
        Load CLIP model + processor with fast tokenizer enabled.
        Removes HF warnings.
        """
        if self.model is not None:
            return

        logger.info(f"Loading CLIP model: {self.model_name}")

        try:
            self.model = CLIPModel.from_pretrained(self.model_name)

            # IMPORTANT: Use fast processors (removes your warning)
            self.processor = CLIPProcessor.from_pretrained(
                self.model_name,
                use_fast=True
            )

            # Move to GPU if available
            if self.device == "cuda":
                try:
                    self.model.to(self.device)
                except Exception:
                    logger.warning("Could not move CLIP to CUDA, using CPU instead.")

            self.model.eval()

            logger.info("CLIP model loaded successfully")

        except Exception as e:
            logger.exception(f"Error loading CLIP model: {e}")
            raise

    def _ensure_rgb(self, image: Image.Image) -> Image.Image:
        """Convert to RGB safely."""
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def extract_embedding(self, image: Image.Image, normalize: bool = True) -> Optional[List[float]]:
        """
        Extract embedding for a single image.
        """
        if self.model is None or self.processor is None:
            self._load_model()

        try:
            image = self._ensure_rgb(image)

            inputs = self.processor(
                images=image,
                return_tensors="pt"
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                features = self.model.get_image_features(**inputs)
                if normalize:
                    features = features / features.norm(dim=-1, keepdim=True)

                embedding = features[0].float().cpu().numpy().tolist()
                return embedding

        except Exception as e:
            logger.exception(f"Failed to extract CLIP embedding: {e}")
            return None

    def extract_embeddings_batch(
        self,
        images: List[Image.Image],
        normalize: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Efficient batch embedding for multiple images.
        """
        if not images:
            return []

        if self.model is None or self.processor is None:
            self._load_model()

        try:
            imgs = [self._ensure_rgb(img) for img in images]

            inputs = self.processor(
                images=imgs,
                return_tensors="pt",
                padding=True
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                feats = self.model.get_image_features(**inputs)

                if normalize:
                    feats = feats / feats.norm(dim=-1, keepdim=True)

                feats = feats.float().cpu().numpy()

                return [feats[i].tolist() for i in range(len(imgs))]

        except Exception as e:
            logger.exception(f"Batch embedding failed: {e}")

            # Fallback per-image (slower)
            return [
                self.extract_embedding(img, normalize=normalize)
                for img in images
            ]

    def extract_text_embedding(self, text: str, normalize: bool = True) -> Optional[List[float]]:
        """
        Extract embedding for a text string.
        """
        if self.model is None or self.processor is None:
            self._load_model()

        try:
            inputs = self.processor(
                text=[text],
                return_tensors="pt",
                padding=True,
                truncation=True
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                text_feat = self.model.get_text_features(**inputs)

                if normalize:
                    text_feat = text_feat / text_feat.norm(dim=-1, keepdim=True)

                return text_feat[0].float().cpu().numpy().tolist()

        except Exception as e:
            logger.exception(f"Text embedding failed: {e}")
            return None
