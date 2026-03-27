"""
Servidor FastAPI para reconhecimento de postura canina em tempo real.
Endpoint principal: POST /predict
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import CORS_ORIGINS
from inference.pipeline import InferencePipeline

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- App FastAPI ---
app = FastAPI(
    title="Dog Posture Recognition API",
    description="API para reconhecimento de postura canina em tempo real usando IA.",
    version="1.0.0",
)

# CORS - permite o frontend React acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pipeline de inferência (singleton)
pipeline = InferencePipeline()


# --- Schemas ---
class PredictRequest(BaseModel):
    image: str  # base64 encoded JPEG

    class Config:
        json_schema_extra = {
            "example": {
                "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
            }
        }


class PredictResponse(BaseModel):
    label: str
    confidence: float
    latency_ms: float
    dog_detected: bool
    smoothed_label: str


# --- Eventos de ciclo de vida ---
@app.on_event("startup")
async def startup_event():
    """Carrega os modelos ao iniciar o servidor."""
    logger.info("Iniciando servidor...")
    try:
        pipeline.load_models()
        logger.info("Servidor pronto para receber requisições.")
    except Exception as e:
        logger.error(f"Erro ao carregar modelos: {e}")
        logger.warning("Servidor iniciado em modo degradado.")


# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Verifica se o servidor está funcionando."""
    return {
        "status": "healthy",
        "models_loaded": pipeline._loaded,
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Recebe um frame em base64 e retorna a predição de postura.

    - **image**: Imagem JPEG codificada em base64
    """
    try:
        result = pipeline.predict(request.image)
        return PredictResponse(**result)
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}",
        )


@app.post("/reset")
async def reset_smoothing():
    """Reseta o histórico de suavização temporal."""
    pipeline.reset_smoothing()
    return {"status": "smoothing history cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
