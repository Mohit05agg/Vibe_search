"""
Object detection using YOLOv8/YOLOv11.
Detects fashion items in images and returns bounding boxes.
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import threading

import torch
from PIL import Image
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not installed. Install with: pip install ultralytics")

logger = logging.getLogger(__name__)

# Global model cache (singleton pattern)
_model_cache: Dict[str, tuple] = {}
_model_lock = threading.Lock()


# Fashion-related COCO classes (YOLO uses COCO dataset)
FASHION_CLASSES = {
    0: 'person',  # Often contains fashion items
    15: 'cat',  # Not fashion, but included for context
    16: 'dog',  # Not fashion, but included for context
    27: 'backpack',
    28: 'umbrella',
    31: 'handbag',
    32: 'tie',
    33: 'suitcase',
    36: 'sports ball',
    39: 'bottle',
    40: 'wine glass',
    41: 'cup',
    42: 'fork',
    43: 'knife',
    44: 'spoon',
    45: 'bowl',
}

# Fashion-specific YOLO models (if available)
FASHION_MODELS = [
    'yolov8n-clothes.pt',  # Custom trained
    'yolov8s-fashion.pt',  # Custom trained
    'yolov8n.pt',  # Fallback to COCO
]

# Custom fashion item mapping (if using custom model)
FASHION_ITEM_MAPPING = {
    'shirt': ['shirt', 't-shirt', 'tshirt', 'top', 'blouse'],
    'pants': ['pants', 'trousers', 'jeans', 'trousers'],
    'shoes': ['shoe', 'sneaker', 'boot', 'sandal', 'heel'],
    'jacket': ['jacket', 'coat', 'blazer'],
    'dress': ['dress', 'gown'],
    'bag': ['bag', 'handbag', 'purse', 'backpack'],
    'hat': ['hat', 'cap', 'beanie'],
    'accessory': ['watch', 'sunglasses', 'jewelry', 'belt'],
}


logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    Object detector using YOLOv8/YOLOv11.
    Detects fashion items in images and returns bounding boxes with class labels.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        model_size: str = 'n',  # n, s, m, l, x
        confidence_threshold: float = 0.25,
        device: Optional[str] = None,
        use_fashion_model: bool = True
    ):
        """
        Initialize object detector with model caching.
        
        Args:
            model_path: Path to custom YOLO model (optional, uses pretrained if None)
            model_size: Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge)
            confidence_threshold: Minimum confidence for detections
            device: Device to use ('cuda', 'cpu', or None for auto)
            use_fashion_model: Try to use fashion-specific model first
        """
        if not YOLO_AVAILABLE:
            raise ImportError(
                "ultralytics not installed. Install with: pip install ultralytics"
            )
        
        self.confidence_threshold = confidence_threshold
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.model_size = model_size
        self.use_fashion_model = use_fashion_model
        
        # Load model with caching
        self.model = self._load_model_cached()
        
        logger.info(f"Object detector initialized on device: {self.device}")
    
    def _load_model_cached(self):
        """Load YOLO model with singleton caching."""
        global _model_cache, _model_lock
        
        # Determine model key
        if self.model_path and Path(self.model_path).exists():
            model_key = self.model_path
        elif self.use_fashion_model:
            # Try fashion models first
            model_key = None
            for fashion_model in FASHION_MODELS:
                if Path(fashion_model).exists():
                    model_key = fashion_model
                    break
            if model_key is None:
                model_key = f'yolov8{self.model_size}.pt'
        else:
            model_key = f'yolov8{self.model_size}.pt'
        
        # Check cache
        with _model_lock:
            if model_key in _model_cache:
                logger.info(f"Using cached YOLO model: {model_key}")
                return _model_cache[model_key]
        
        # Load new model
        try:
            if self.model_path and Path(self.model_path).exists():
                logger.info(f"Loading custom YOLO model from {self.model_path}")
                model = YOLO(self.model_path)
            elif self.use_fashion_model:
                # Try fashion models
                model = None
                for fashion_model in FASHION_MODELS:
                    if Path(fashion_model).exists():
                        logger.info(f"Loading fashion YOLO model: {fashion_model}")
                        model = YOLO(fashion_model)
                        break
                
                if model is None:
                    logger.info(f"Fashion models not found, using default: yolov8{self.model_size}.pt")
                    model = YOLO(f'yolov8{self.model_size}.pt')
            else:
                model_name = f'yolov8{self.model_size}.pt'
                logger.info(f"Loading pretrained YOLO model: {model_name}")
                model = YOLO(model_name)
            
            # Move to device
            if self.device == 'cuda' and torch.cuda.is_available():
                model.to(self.device)
            
            # Cache model
            with _model_lock:
                _model_cache[model_key] = model
            
            return model
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            raise
    
    def detect(
        self,
        image: Image.Image,
        return_crops: bool = True
    ) -> List[Dict]:
        """
        Detect objects in image.
        
        Args:
            image: PIL Image
            return_crops: Whether to return cropped images of detected objects
            
        Returns:
            List of detection dictionaries with keys:
            - class_id: COCO class ID
            - class_name: Class name
            - confidence: Detection confidence (0-1)
            - bbox: [x1, y1, x2, y2] bounding box coordinates
            - crop: Cropped PIL Image (if return_crops=True)
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        try:
            # Run detection
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is None or len(boxes) == 0:
                    continue
                
                for box in boxes:
                    # Get bounding box coordinates (xyxy format)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Filter for fashion-related items or person (which often contains fashion)
                    if class_id in FASHION_CLASSES or class_id == 0:  # person
                        detection = {
                            'class_id': class_id,
                            'class_name': class_name,
                            'confidence': confidence,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        }
                        
                        # Crop object if requested
                        if return_crops:
                            try:
                                crop = image.crop((int(x1), int(y1), int(x2), int(y2)))
                                detection['crop'] = crop
                            except Exception as e:
                                logger.warning(f"Error cropping image: {e}")
                                detection['crop'] = None
                        
                        detections.append(detection)
            
            # Map to fashion items if possible
            detections = self._map_to_fashion_items(detections)
            
            # Return in standard format
            return self._format_detections(detections)
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []
    
    def _map_to_fashion_items(self, detections: List[Dict]) -> List[Dict]:
        """
        Map detected objects to fashion item categories.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List with added 'detected_class' field
        """
        for detection in detections:
            class_name = detection['class_name'].lower()
            detected_class = None
            
            # Map to fashion categories
            for fashion_class, keywords in FASHION_ITEM_MAPPING.items():
                if any(keyword in class_name for keyword in keywords):
                    detected_class = fashion_class
                    break
            
            # If person detected, try to infer from context
            if detection['class_id'] == 0:  # person
                detected_class = 'outfit'  # Default for person images
            
            # Use class name as fallback
            if detected_class is None:
                detected_class = class_name
            
            detection['detected_class'] = detected_class
        
        return detections
    
    def _format_detections(self, detections: List[Dict]) -> List[Dict]:
        """
        Format detections to standard structure.
        
        Returns:
            List with standard format: {labels, boxes, scores, detected_class, crop}
        """
        formatted = []
        for det in detections:
            formatted.append({
                'labels': [det['class_name']],
                'boxes': [det['bbox']],  # [x1, y1, x2, y2]
                'scores': [det['confidence']],
                'detected_class': det.get('detected_class', det['class_name']),
                'bbox': det['bbox'],
                'confidence': det['confidence'],
                'crop': det.get('crop')
            })
        return formatted
    
    def get_primary_detection(self, image: Image.Image) -> Optional[Dict]:
        """
        Get the primary (most confident) detection from image.
        
        Args:
            image: PIL Image
            
        Returns:
            Detection dictionary or None
        """
        detections = self.detect(image, return_crops=True)
        
        if not detections:
            return None
        
        # Return most confident detection
        return max(detections, key=lambda x: x['confidence'])

