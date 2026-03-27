"""
Configurações centrais do sistema de reconhecimento de postura canina.
"""
import os

# --- Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Caminho do modelo de classificação treinado
CLASSIFIER_WEIGHTS = os.path.join(MODELS_DIR, "posture_classifier.pth")
CLASSIFIER_ONNX = os.path.join(MODELS_DIR, "posture_classifier.onnx")

# Caminho do dataset
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# --- Classes de postura ---
CLASS_NAMES = ["DEITADO", "EM_PE", "SENTADO"]
NUM_CLASSES = len(CLASS_NAMES)

# --- Preprocessamento de imagem ---
IMAGE_SIZE = 224  # MobileNetV2 input size
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# --- Detecção (YOLOv8) ---
YOLO_MODEL = "yolov8n.pt"  # nano model (~6MB)
DOG_CLASS_ID = 16  # COCO class ID for 'dog'
DETECTION_CONFIDENCE = 0.3

# --- Inferência ---
CONFIDENCE_THRESHOLD = 0.5
SMOOTHING_WINDOW = 5  # número de frames para suavização temporal

# --- Treinamento ---
BATCH_SIZE = 32
LEARNING_RATE = 1e-3
FINE_TUNE_LR = 1e-4
NUM_EPOCHS = 20
FINE_TUNE_EPOCHS = 10
EARLY_STOPPING_PATIENCE = 5
TRAIN_SPLIT = 0.8

# --- API ---
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
