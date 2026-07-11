"""
TCC - Reconhecimento de Postura de Cães
Backend FastAPI - Servidor principal
"""

import json
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from services.inference_service import InferenceService

METRICS_PATH = Path(__file__).resolve().parent / "models" / "metrics.json"


# Inicialização do serviço de inferência
inference_service = InferenceService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup: carrega o modelo
    print("🐶 Carregando modelo de classificação de postura...")
    inference_service.load_model()
    print("✅ Modelo carregado com sucesso!")
    yield
    # Shutdown
    print("👋 Encerrando servidor...")


app = FastAPI(
    title="TCC - Classificação de Postura de Cães",
    description="API para reconhecimento de postura de cães em tempo real",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuração de CORS para permitir requisições do frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde do servidor.
    Retorna o status do servidor e se o modelo está carregado.
    """
    return {
        "status": "online",
        "model_loaded": inference_service.is_model_loaded(),
        "model_type": inference_service.get_model_info(),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Endpoint principal de predição.

    Recebe uma imagem (frame da webcam) e retorna:
    - label: classe prevista (EM_PE, SENTADO, DEITADO)
    - confidence: confiança da predição (0.0 a 1.0)
    - latency_ms: tempo de inferência em milissegundos
    """
    start_time = time.time()

    try:
        image_bytes = await file.read()
        result = inference_service.predict(image_bytes)
    except Exception as e:
        result = {"label": "ERRO", "confidence": 0.0, "error": str(e)}

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "label": result["label"],
        "confidence": result["confidence"],
        "latency_ms": latency_ms,
    }


@app.get("/metrics")
async def get_metrics():
    """
    Métricas de avaliação do modelo treinado, geradas por
    backend/training/evaluate.py no split de teste (held-out): acurácia,
    precisão/recall/F1 por classe, matriz de confusão e latência média.
    """
    if not METRICS_PATH.exists():
        return {"available": False}

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    return {"available": True, **metrics}
