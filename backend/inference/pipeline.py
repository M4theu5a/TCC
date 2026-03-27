"""
Pipeline principal de inferência.
Orquestra: decodificação → detecção → recorte → pré-processamento → classificação.
Inclui suavização temporal para reduzir oscilações.
"""
import logging
import time
from collections import deque
from statistics import mode

from PIL import Image

from config import SMOOTHING_WINDOW, CLASS_NAMES
from inference.preprocessor import decode_base64_image, preprocess_image, crop_image
from inference.detector import DogDetector
from inference.classifier import PostureClassifier

logger = logging.getLogger(__name__)


class InferencePipeline:
    """Pipeline completo de inferência com suavização temporal."""

    def __init__(self):
        self.detector = DogDetector()
        self.classifier = PostureClassifier()
        self.prediction_history = deque(maxlen=SMOOTHING_WINDOW)
        self._loaded = False

    def load_models(self):
        """Carrega todos os modelos na memória."""
        logger.info("Inicializando pipeline de inferência...")
        self.detector.load()
        self.classifier.load()
        self._loaded = True
        logger.info("Pipeline de inferência pronto.")

    def predict(self, base64_image: str) -> dict:
        """
        Executa o pipeline completo de inferência.

        Args:
            base64_image: Imagem codificada em base64 (JPEG)

        Returns:
            dict com 'label', 'confidence', 'latency_ms', 'dog_detected',
            'smoothed_label'
        """
        if not self._loaded:
            self.load_models()

        start_time = time.time()

        # 1. Decodificar imagem
        image = decode_base64_image(base64_image)

        # 2. Detectar cão no frame
        detection = self.detector.detect(image)
        dog_detected = detection is not None

        # 3. Recortar região do cão (ou usar frame inteiro)
        if dog_detected:
            cropped = crop_image(image, detection["bbox"])
        else:
            cropped = image

        # 4. Pré-processar para o classificador
        tensor = preprocess_image(cropped)

        # 5. Classificar postura
        result = self.classifier.predict(tensor)

        # 6. Suavização temporal
        self.prediction_history.append(result["class_index"])
        smoothed_label = self._get_smoothed_label()

        # 7. Calcular latência
        latency_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "label": result["label"],
            "confidence": result["confidence"],
            "latency_ms": latency_ms,
            "dog_detected": dog_detected,
            "smoothed_label": smoothed_label,
        }

    def _get_smoothed_label(self) -> str:
        """
        Retorna o label mais frequente na janela de suavização.
        Reduz oscilações rápidas entre classes.
        """
        if not self.prediction_history:
            return CLASS_NAMES[0]

        try:
            most_common = mode(self.prediction_history)
        except Exception:
            # Se não há moda clara, usa a predição mais recente
            most_common = self.prediction_history[-1]

        return CLASS_NAMES[most_common]

    def reset_smoothing(self):
        """Limpa o histórico de suavização."""
        self.prediction_history.clear()
