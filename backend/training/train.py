"""
Script de treinamento do classificador de postura canina.
Usa MobileNetV2 com transfer learning em duas fases:
  1. Treina apenas a camada classificadora (backbone congelado)
  2. Fine-tuning das últimas camadas do backbone

Uso:
    cd c:\\Tcc\\backend
    python -m training.train
"""
import os
import time
import copy

import torch
import torch.nn as nn
import torch.optim as optim

from config import (
    MODELS_DIR,
    CLASSIFIER_WEIGHTS,
    NUM_EPOCHS,
    FINE_TUNE_EPOCHS,
    LEARNING_RATE,
    FINE_TUNE_LR,
    EARLY_STOPPING_PATIENCE,
)
from inference.classifier import create_model
from training.dataset import load_datasets


def train_one_epoch(model, loader, criterion, optimizer, device):
    """Treina o modelo por uma época."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100.0 * correct / total
    return epoch_loss, epoch_acc


def validate(model, loader, criterion, device):
    """Avalia o modelo no conjunto de validação."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100.0 * correct / total
    return epoch_loss, epoch_acc


def freeze_backbone(model):
    """Congela todas as camadas exceto o classificador."""
    for param in model.features.parameters():
        param.requires_grad = False


def unfreeze_last_layers(model, num_layers=3):
    """Descongela as últimas N camadas do backbone para fine-tuning."""
    children = list(model.features.children())
    for child in children[-num_layers:]:
        for param in child.parameters():
            param.requires_grad = True


def train():
    """Pipeline completo de treinamento."""
    print("=" * 60)
    print("TREINAMENTO - Classificador de Postura Canina")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDispositivo: {device}")

    # Carregar datasets
    train_loader, val_loader, class_names = load_datasets()
    print(f"Classes: {class_names}")

    # Criar modelo
    model = create_model()
    model.to(device)

    criterion = nn.CrossEntropyLoss()

    # =============================================
    # FASE 1: Treinar apenas o classificador
    # =============================================
    print("\n" + "=" * 60)
    print("FASE 1: Treinando camada classificadora (backbone congelado)")
    print("=" * 60)

    freeze_backbone(model)
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LEARNING_RATE,
    )

    best_model_wts = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(NUM_EPOCHS):
        start = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        elapsed = time.time() - start

        print(
            f"Época {epoch+1:02d}/{NUM_EPOCHS} | "
            f"Treino: loss={train_loss:.4f} acc={train_acc:.1f}% | "
            f"Val: loss={val_loss:.4f} acc={val_acc:.1f}% | "
            f"Tempo: {elapsed:.1f}s"
        )

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print(f"\nEarly stopping na época {epoch+1}")
                break

    model.load_state_dict(best_model_wts)

    # =============================================
    # FASE 2: Fine-tuning das últimas camadas
    # =============================================
    print("\n" + "=" * 60)
    print("FASE 2: Fine-tuning (últimas 3 camadas desbloqueadas)")
    print("=" * 60)

    unfreeze_last_layers(model, num_layers=3)
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=FINE_TUNE_LR,
    )

    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(FINE_TUNE_EPOCHS):
        start = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        elapsed = time.time() - start

        print(
            f"Fine-tune {epoch+1:02d}/{FINE_TUNE_EPOCHS} | "
            f"Treino: loss={train_loss:.4f} acc={train_acc:.1f}% | "
            f"Val: loss={val_loss:.4f} acc={val_acc:.1f}% | "
            f"Tempo: {elapsed:.1f}s"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print(f"\nEarly stopping no fine-tune {epoch+1}")
                break

    model.load_state_dict(best_model_wts)

    # Salvar modelo
    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(model.state_dict(), CLASSIFIER_WEIGHTS)
    print(f"\nModelo salvo em: {CLASSIFIER_WEIGHTS}")
    print("=" * 60)
    print("TREINAMENTO CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    train()
