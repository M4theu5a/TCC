"""
Pré-processamento de imagens para inferência.
Decodifica base64, redimensiona e normaliza para o formato esperado pelo modelo.
"""
import base64
import io

import numpy as np
from PIL import Image
from torchvision import transforms

from config import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD


def get_transform():
    """Retorna o pipeline de transformação para inferência."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    Decodifica uma string base64 para PIL Image.
    Aceita com ou sem o prefixo 'data:image/...;base64,'.
    """
    # Remove o prefixo data URI se presente
    if "," in base64_string:
        base64_string = base64_string.split(",", 1)[1]

    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return image


def preprocess_image(image: Image.Image):
    """
    Aplica transformações na imagem e retorna tensor pronto para o modelo.
    Retorna tensor com shape (1, 3, 224, 224).
    """
    transform = get_transform()
    tensor = transform(image)
    return tensor.unsqueeze(0)  # Adiciona dimensão do batch


def crop_image(image: Image.Image, bbox: list) -> Image.Image:
    """
    Recorta a imagem na região do bounding box.
    bbox formato: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = [int(v) for v in bbox]
    return image.crop((x1, y1, x2, y2))
