"""
Serviço de Inferência - Classificação de Postura de Cães

Carrega o modelo treinado (backend/models/dog_posture_model.pth, gerado por
backend/training/train.py) e realiza a classificação real. Se o checkpoint
não existir ou falhar ao carregar, cai automaticamente para um stub
(predição simulada) em vez de derrubar o servidor.
"""

import io
import random
import time
from pathlib import Path

import torch
from PIL import Image
from PIL import UnidentifiedImageError

from services.model_arch import build_model
from services.preprocessing import build_eval_transform

# As classes de postura que o modelo reconhece
CLASSES = ["EM_PE", "SENTADO", "DEITADO"]

# Labels amigáveis para exibição
LABELS_PT = {
    "EM_PE": "Em Pé",
    "SENTADO": "Sentado",
    "DEITADO": "Deitado",
}

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "dog_posture_model.pth"


class InferenceService:
    """
    Serviço responsável por carregar o modelo e realizar inferências.

    Tenta carregar o modelo real treinado (MobileNetV2 + Transfer Learning).
    Se o checkpoint não existir ou falhar ao carregar, cai para um stub
    (predição aleatória) para o servidor continuar funcionando.
    """

    def __init__(self):
        self._model = None
        self._transform = None
        self._model_loaded = False
        self._use_stub = True

    def load_model(self):
        """Carrega o modelo real; em caso de falha, cai para o modo stub."""
        try:
            self._load_real_model()
            self._use_stub = False
            self._model_loaded = True
        except Exception as e:
            print(f"⚠️  Não foi possível carregar o modelo treinado: {e}")
            print("⚠️  Usando modo STUB (predição simulada)")
            self._use_stub = True
            self._model_loaded = True

    def _load_real_model(self):
        """Carrega os pesos treinados a partir de MODEL_PATH."""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Checkpoint não encontrado em {MODEL_PATH}. "
                "Rode 'python training/train.py' (a partir de backend/) para treinar o modelo."
            )

        model = build_model(num_classes=len(CLASSES), pretrained=False, freeze_backbone=False)
        state_dict = torch.load(MODEL_PATH, map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()

        self._model = model
        self._transform = build_eval_transform()

    def is_model_loaded(self) -> bool:
        """Retorna se o modelo está carregado (real ou stub)."""
        return self._model_loaded

    def get_model_info(self) -> str:
        """Retorna informação sobre o tipo de modelo em uso."""
        if self._use_stub:
            return "stub (simulado)"
        return "modelo_treinado"

    def preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """Converte os bytes recebidos em uma imagem PIL RGB."""
        image = Image.open(io.BytesIO(image_bytes))
        return image.convert("RGB")

    def predict(self, image_bytes: bytes) -> dict:
        """
        Realiza a predição da postura do cão.

        Args:
            image_bytes: bytes da imagem (frame da webcam)

        Returns:
            Dicionário com label, confidence e, em caso de erro, error.
        """
        if not self._model_loaded:
            return {
                "label": "ERRO",
                "confidence": 0.0,
                "error": "Modelo não carregado",
            }

        try:
            image = self.preprocess_image(image_bytes)
        except (UnidentifiedImageError, OSError) as e:
            return {
                "label": "ERRO",
                "confidence": 0.0,
                "error": f"Erro no pré-processamento: {str(e)}",
            }

        if self._use_stub:
            return self._predict_stub()

        try:
            return self._predict_real(image)
        except Exception as e:
            return {
                "label": "ERRO",
                "confidence": 0.0,
                "error": f"Erro na inferência: {str(e)}",
            }

    def _predict_stub(self) -> dict:
        """
        Predição simulada, usada apenas como fallback quando o modelo real
        não pôde ser carregado.
        """
        time.sleep(random.uniform(0.02, 0.08))

        label = random.choices(CLASSES, weights=[0.4, 0.35, 0.25], k=1)[0]
        confidence = round(random.uniform(0.60, 0.98), 2)

        return {
            "label": label,
            "confidence": confidence,
        }

    def _predict_real(self, image: Image.Image) -> dict:
        """Predição real com o modelo treinado (MobileNetV2 fine-tuned)."""
        tensor = self._transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = self._model(tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        return {
            "label": CLASSES[predicted.item()],
            "confidence": round(confidence.item(), 2),
        }
