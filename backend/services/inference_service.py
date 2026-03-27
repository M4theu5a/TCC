"""
Serviço de Inferência - Classificação de Postura de Cães

Este módulo contém a lógica de inferência do modelo.
No MVP, utiliza um stub (predição simulada).
Na versão final, carregará o modelo treinado com PyTorch/TorchVision.
"""

import io
import time
import random
from PIL import Image
import numpy as np

# As classes de postura que o modelo reconhece
CLASSES = ["EM_PE", "SENTADO", "DEITADO"]

# Labels amigáveis para exibição
LABELS_PT = {
    "EM_PE": "Em Pé",
    "SENTADO": "Sentado",
    "DEITADO": "Deitado",
}


class InferenceService:
    """
    Serviço responsável por carregar o modelo e realizar inferências.
    
    No MVP, retorna predições simuladas (stub).
    Quando o modelo estiver treinado, basta implementar os métodos
    _load_real_model() e _predict_real().
    """

    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._use_stub = True  # Mude para False quando tiver o modelo treinado
        self._image_size = (224, 224)  # Tamanho padrão para CNNs

    def load_model(self):
        """
        Carrega o modelo de classificação.
        No modo stub, apenas marca como carregado.
        """
        if self._use_stub:
            print("⚠️  Usando modo STUB (predição simulada)")
            print("   Para usar o modelo real, defina self._use_stub = False")
            self._model_loaded = True
        else:
            self._load_real_model()

    def _load_real_model(self):
        """
        Carrega o modelo real treinado.
        
        TODO: Implementar quando o modelo estiver treinado.
        Exemplo com PyTorch:
        
        import torch
        import torchvision.models as models
        
        self._model = models.mobilenet_v2(pretrained=False)
        self._model.classifier[1] = torch.nn.Linear(
            self._model.last_channel, len(CLASSES)
        )
        self._model.load_state_dict(torch.load("models/dog_posture_model.pth"))
        self._model.eval()
        self._model_loaded = True
        """
        raise NotImplementedError(
            "Modelo real ainda não implementado. Use o modo stub."
        )

    def is_model_loaded(self) -> bool:
        """Retorna se o modelo está carregado."""
        return self._model_loaded

    def get_model_info(self) -> str:
        """Retorna informação sobre o tipo de modelo em uso."""
        if self._use_stub:
            return "stub (simulado)"
        return "modelo_treinado"

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Pré-processa a imagem recebida.
        
        Etapas:
        1. Converte bytes para imagem PIL
        2. Redimensiona para o tamanho esperado pelo modelo
        3. Converte para array numpy
        4. Normaliza os valores dos pixels (0-1)
        
        Args:
            image_bytes: bytes da imagem recebida
            
        Returns:
            Array numpy com a imagem pré-processada
        """
        # Abre a imagem a partir dos bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Converte para RGB (caso venha em outro formato)
        image = image.convert("RGB")

        # Redimensiona para o tamanho esperado pelo modelo
        image = image.resize(self._image_size)

        # Converte para numpy array e normaliza (0 a 1)
        image_array = np.array(image, dtype=np.float32) / 255.0

        return image_array

    def predict(self, image_bytes: bytes) -> dict:
        """
        Realiza a predição da postura do cão.
        
        Args:
            image_bytes: bytes da imagem (frame da webcam)
            
        Returns:
            Dicionário com label, confidence e detalhes
        """
        if not self._model_loaded:
            return {
                "label": "ERRO",
                "confidence": 0.0,
                "error": "Modelo não carregado",
            }

        # Pré-processa a imagem (mesmo no stub, para validar o pipeline)
        try:
            image_array = self.preprocess_image(image_bytes)
        except Exception as e:
            return {
                "label": "ERRO",
                "confidence": 0.0,
                "error": f"Erro no pré-processamento: {str(e)}",
            }

        if self._use_stub:
            return self._predict_stub(image_array)
        else:
            return self._predict_real(image_array)

    def _predict_stub(self, image_array: np.ndarray) -> dict:
        """
        Predição simulada para o MVP.
        
        Retorna uma classe aleatória com confiança simulada.
        Útil para testar o pipeline completo (frontend → backend → resposta)
        antes de ter o modelo treinado.
        """
        # Simula um pequeno delay de inferência
        time.sleep(random.uniform(0.02, 0.08))

        # Escolhe uma classe aleatória com pesos (para simular algo mais realista)
        label = random.choices(
            CLASSES,
            weights=[0.4, 0.35, 0.25],  # Probabilidades de cada classe
            k=1,
        )[0]

        # Gera uma confiança simulada (entre 0.6 e 0.98)
        confidence = round(random.uniform(0.60, 0.98), 2)

        return {
            "label": label,
            "confidence": confidence,
        }

    def _predict_real(self, image_array: np.ndarray) -> dict:
        """
        Predição real com o modelo treinado.
        
        TODO: Implementar quando o modelo estiver pronto.
        
        Exemplo:
        
        import torch
        import torchvision.transforms as transforms
        
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])
        
        tensor = transform(image_array).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self._model(tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        return {
            "label": CLASSES[predicted.item()],
            "confidence": round(confidence.item(), 2),
        }
        """
        raise NotImplementedError("Modelo real não implementado ainda.")
