"""
Transforms de pré-processamento de imagem.

`build_eval_transform()` é usado tanto pela inferência em produção
(services/inference_service.py) quanto pela avaliação/validação do treino
(backend/training/), para garantir que uma imagem seja processada
exatamente da mesma forma nos dois contextos.
"""

import torchvision.transforms as transforms

IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_eval_transform() -> transforms.Compose:
    """Transform usado em validação, teste e inferência em produção."""
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def build_train_transform() -> transforms.Compose:
    """Transform usado em treino, com augmentação de dados."""
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
