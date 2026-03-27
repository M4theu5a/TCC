"""
Detecção de cães usando YOLOv8-nano.
Localiza o cão no frame antes da classificação de postura.
"""
import logging

from ultralytics import YOLO

from config import YOLO_MODEL, DOG_CLASS_ID, DETECTION_CONFIDENCE

logger = logging.getLogger(__name__)


class DogDetector:
    """Detecta cães em imagens usando YOLOv8."""

    def __init__(self):
        self.model = None

    def load(self):
        """Carrega o modelo YOLOv8-nano. Faz download automático na primeira vez."""
        logger.info("Carregando modelo YOLOv8-nano...")
        self.model = YOLO(YOLO_MODEL)
        logger.info("YOLOv8-nano carregado com sucesso.")

    def detect(self, image) -> dict | None:
        """
        Detecta o cão com maior confiança na imagem.

        Args:
            image: PIL Image

        Returns:
            dict com 'bbox' [x1,y1,x2,y2] e 'confidence', ou None se nenhum cão detectado.
        """
        if self.model is None:
            self.load()

        results = self.model(image, verbose=False, conf=DETECTION_CONFIDENCE)

        best_detection = None
        best_conf = 0.0

        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())

                if cls_id == DOG_CLASS_ID and conf > best_conf:
                    best_conf = conf
                    bbox = boxes.xyxy[i].tolist()
                    best_detection = {
                        "bbox": bbox,
                        "confidence": best_conf,
                    }

        if best_detection:
            logger.debug(
                f"Cão detectado com confiança {best_detection['confidence']:.2f}"
            )
        else:
            logger.debug("Nenhum cão detectado no frame.")

        return best_detection
