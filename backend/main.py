"""
TCC - Reconhecimento de Postura de Cães
Backend FastAPI - Servidor principal
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from services.inference_service import InferenceService


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

    # Lê os bytes da imagem enviada
    image_bytes = await file.read()

    # Realiza a inferência
    result = inference_service.predict(image_bytes)

    # Calcula a latência total
    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "label": result["label"],
        "confidence": result["confidence"],
        "latency_ms": latency_ms,
    }
