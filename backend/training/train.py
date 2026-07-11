"""
Treino do classificador de postura (Transfer Learning sobre MobileNetV2).

Uso: a partir de backend/
    python training/train.py
"""

import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.inference_service import CLASSES  # noqa: E402
from services.model_arch import build_model  # noqa: E402
from dataset import load_splits  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "dog_posture_model.pth"
BATCH_SIZE = 32
NUM_EPOCHS = 12
LEARNING_RATE = 1e-3
NUM_WORKERS = 4
SEED = 42


def _evaluate(model, loader, device) -> float:
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            predicted = outputs.argmax(dim=1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return correct / total if total else 0.0


def main():
    torch.manual_seed(SEED)
    device = torch.device("cpu")

    print("Carregando dataset...")
    train_ds, val_ds, _test_ds = load_splits()

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)

    print("Construindo modelo (MobileNetV2, backbone congelada)...")
    model = build_model(num_classes=len(CLASSES), pretrained=True, freeze_backbone=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    best_val_acc = 0.0

    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        epoch_start = time.time()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        train_loss = running_loss / len(train_ds)
        val_acc = _evaluate(model, val_loader, device)
        epoch_time = time.time() - epoch_start

        marker = ""
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_PATH)
            marker = " (novo melhor, salvo)"

        print(
            f"Epoca {epoch:02d}/{NUM_EPOCHS} | loss={train_loss:.4f} "
            f"| val_acc={val_acc:.4f} | {epoch_time:.1f}s{marker}"
        )

    print(f"\nTreino concluido. Melhor val_acc={best_val_acc:.4f}. Modelo salvo em {MODEL_PATH}")


if __name__ == "__main__":
    main()
