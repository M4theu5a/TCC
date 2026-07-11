# Diagrama de Arquitetura

## Fluxo de inferência (produção)

```mermaid
flowchart LR
    A[Webcam] -->|getUserMedia| B[React: WebcamCapture]
    B -->|Canvas captura frame| C[Blob JPEG]
    C -->|POST /predict| D[FastAPI]
    D --> E[InferenceService.predict]
    E --> F[Pré-processamento<br/>Resize 224x224 + Normalize ImageNet]
    F --> G[MobileNetV2<br/>backbone congelada + head treinada]
    G --> H[Softmax → label + confidence]
    H -->|JSON: label, confidence, latency_ms| B
    B --> I[Overlay em tempo real<br/>+ Métricas + Histórico]
```

## Pipeline de treino (offline, backend/training/)

```mermaid
flowchart TD
    A[Hugging Face Hub<br/>stockeh/dog-pose-cv] -->|data/images.tar.gz<br/>data/labels.tar.gz| B[dataset.py]
    B --> C[Filtra 'undefined'<br/>Balanceia 3000/classe<br/>Split 70/15/15]
    C --> D[train.py<br/>MobileNetV2 + Transfer Learning<br/>12 épocas, Adam lr=1e-3]
    D --> E[backend/models/dog_posture_model.pth]
    C --> F[evaluate.py<br/>Avaliação no split de teste]
    E --> F
    F --> G[backend/models/metrics.json]
    F --> H[docs/tcc/resultados/<br/>confusion_matrix.png<br/>classification_report.txt]
```

## Componentes

| Componente | Responsabilidade |
|---|---|
| `frontend/src/components/WebcamCapture.jsx` | Captura de frames da webcam via Canvas |
| `frontend/src/services/api.js` | Comunicação HTTP com o backend (axios) |
| `backend/main.py` | Endpoints REST (`/health`, `/predict`, `/metrics`) |
| `backend/services/inference_service.py` | Orquestra pré-processamento + inferência |
| `backend/services/model_arch.py` | Definição única da arquitetura (usada por treino e produção) |
| `backend/services/preprocessing.py` | Transforms únicos (usados por treino e produção) |
| `backend/training/` | Pipeline offline de download, treino e avaliação |
