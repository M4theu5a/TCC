"""
Classificador de postura canina baseado em MobileNetV2 com transfer learning.
"""
import logging
import os

import torch
import torch.nn as nn
from torchvision import models

from config import NUM_CLASSES, CLASS_NAMES, CLASSIFIER_WEIGHTS, CLASSIFIER_ONNX

logger = logging.getLogger(__name__)


def create_model(num_classes: int = NUM_CLASSES) -> nn.Module:
    """
    Cria o modelo MobileNetV2 com a camada de classificação customizada.
    Usado tanto para treinamento quanto para inferência.
    """
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    # Substitui a camada classificadora final
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(model.last_channel, num_classes),
    )

    return model


class PostureClassifier:
    """Classifica a postura do cão a partir de uma imagem pré-processada."""

    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_onnx = False
        self.onnx_session = None

    def load(self):
        """Carrega os pesos do modelo treinado."""
        # Tenta carregar ONNX primeiro (mais rápido para inferência)
        if os.path.exists(CLASSIFIER_ONNX):
            self._load_onnx()
            return

        if os.path.exists(CLASSIFIER_WEIGHTS):
            self._load_pytorch()
            return

        # Modo stub: carrega MobileNetV2 sem pesos customizados
        logger.warning(
            "Nenhum modelo treinado encontrado. Usando modo STUB (previsões não confiáveis)."
        )
        self.model = create_model()
        self.model.to(self.device)
        self.model.eval()

    def _load_pytorch(self):
        """Carrega modelo PyTorch."""
        logger.info(f"Carregando modelo PyTorch de {CLASSIFIER_WEIGHTS}")
        self.model = create_model()
        state_dict = torch.load(CLASSIFIER_WEIGHTS, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        self.use_onnx = False
        logger.info("Modelo PyTorch carregado com sucesso.")

    def _load_onnx(self):
        """Carrega modelo ONNX para inferência otimizada."""
        import onnxruntime as ort

        logger.info(f"Carregando modelo ONNX de {CLASSIFIER_ONNX}")
        self.onnx_session = ort.InferenceSession(
            CLASSIFIER_ONNX,
            providers=["CPUExecutionProvider"],
        )
        self.use_onnx = True
        logger.info("Modelo ONNX carregado com sucesso.")

    def predict(self, tensor) -> dict:
        """
        Realiza a classificação da postura.

        Args:
            tensor: Tensor pré-processado com shape (1, 3, 224, 224)

        Returns:
            dict com 'label' (str), 'confidence' (float), 'class_index' (int)
        """
        if self.use_onnx and self.onnx_session is not None:
            return self._predict_onnx(tensor)
        return self._predict_pytorch(tensor)

    def _predict_pytorch(self, tensor) -> dict:
        """Inferência usando PyTorch."""
        if self.model is None:
            self.load()

        tensor = tensor.to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, class_idx = torch.max(probabilities, dim=1)

        class_index = class_idx.item()
        return {
            "label": CLASS_NAMES[class_index],
            "confidence": round(confidence.item(), 4),
            "class_index": class_index,
        }

    def _predict_onnx(self, tensor) -> dict:
        """Inferência usando ONNX Runtime (mais rápida)."""
        import numpy as np

        input_array = tensor.numpy()
        input_name = self.onnx_session.get_inputs()[0].name
        outputs = self.onnx_session.run(None, {input_name: input_array})

        logits = outputs[0][0]
        # Softmax manual
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()

        class_index = int(np.argmax(probabilities))
        confidence = float(probabilities[class_index])

        return {
            "label": CLASS_NAMES[class_index],
            "confidence": round(confidence, 4),
            "class_index": class_index,
        }
