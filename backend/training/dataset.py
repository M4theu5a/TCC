"""
Dataset loader com data augmentation para treinamento do classificador de postura.
Espera estrutura de diretórios:
    dataset/
        DEITADO/
            img001.jpg
            ...
        EM_PE/
            img001.jpg
            ...
        SENTADO/
            img001.jpg
            ...
"""
import os

from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

from config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    BATCH_SIZE,
    TRAIN_SPLIT,
    DATASET_DIR,
)


def get_train_transform():
    """Transformações com data augmentation para treinamento."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
        transforms.RandomCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.2,
            hue=0.1,
        ),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transform():
    """Transformações para validação (sem augmentation)."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def load_datasets(dataset_dir: str = DATASET_DIR):
    """
    Carrega o dataset e divide em treino/validação.

    Args:
        dataset_dir: Caminho para o diretório com as classes.

    Returns:
        (train_loader, val_loader, class_names)
    """
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(
            f"Diretório do dataset não encontrado: {dataset_dir}\n"
            "Crie o diretório com subpastas: DEITADO/, EM_PE/, SENTADO/\n"
            "Ou execute: python training/prepare_dataset.py"
        )

    # Carrega dataset completo com transformação de treino
    full_dataset = datasets.ImageFolder(dataset_dir, transform=get_train_transform())
    class_names = full_dataset.classes

    print(f"\nDataset carregado:")
    print(f"  Total de imagens: {len(full_dataset)}")
    print(f"  Classes: {class_names}")

    # Conta imagens por classe
    for i, name in enumerate(class_names):
        count = sum(1 for _, label in full_dataset if label == i)
        print(f"  {name}: {count} imagens")

    # Divide em treino/validação
    train_size = int(len(full_dataset) * TRAIN_SPLIT)
    val_size = len(full_dataset) - train_size

    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # Aplica transformação de validação no conjunto de validação
    val_dataset.dataset = datasets.ImageFolder(
        dataset_dir, transform=get_val_transform()
    )

    print(f"  Treino: {train_size} imagens")
    print(f"  Validação: {val_size} imagens\n")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,  # Windows compatibility
        pin_memory=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=True,
    )

    return train_loader, val_loader, class_names
