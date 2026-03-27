"""
Script de avaliação do modelo treinado.
Gera métricas de classificação e matriz de confusão.

Uso:
    cd c:\\Tcc\\backend
    python -m training.evaluate
"""
import os
import time

import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

from config import CLASSIFIER_WEIGHTS, CLASS_NAMES, MODELS_DIR
from inference.classifier import create_model
from training.dataset import load_datasets


def evaluate():
    """Avalia o modelo e gera relatório completo."""
    print("=" * 60)
    print("AVALIAÇÃO - Classificador de Postura Canina")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Dispositivo: {device}")

    # Carregar modelo
    if not os.path.exists(CLASSIFIER_WEIGHTS):
        print(f"ERRO: Modelo não encontrado em {CLASSIFIER_WEIGHTS}")
        print("Execute primeiro: python -m training.train")
        return

    model = create_model()
    model.load_state_dict(torch.load(CLASSIFIER_WEIGHTS, map_location=device))
    model.to(device)
    model.eval()

    # Carregar dados de validação
    _, val_loader, class_names = load_datasets()

    # Coletar predições
    all_labels = []
    all_preds = []
    latencies = []

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)

            start = time.time()
            outputs = model(images)
            latency = (time.time() - start) * 1000  # ms

            _, predicted = outputs.max(1)

            all_labels.extend(labels.numpy())
            all_preds.extend(predicted.cpu().numpy())
            latencies.append(latency)

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)

    # --- Relatório de classificação ---
    print("\n" + "=" * 60)
    print("RELATÓRIO DE CLASSIFICAÇÃO")
    print("=" * 60)
    print(classification_report(
        all_labels,
        all_preds,
        target_names=CLASS_NAMES,
        digits=4,
    ))

    # --- Acurácia geral ---
    accuracy = (all_labels == all_preds).mean() * 100
    print(f"Acurácia geral: {accuracy:.2f}%")

    # --- Métricas de latência ---
    print("\n--- Métricas de Latência ---")
    print(f"Latência média: {np.mean(latencies):.1f} ms")
    print(f"Latência mediana: {np.median(latencies):.1f} ms")
    print(f"Latência máxima: {np.max(latencies):.1f} ms")
    print(f"Latência mínima: {np.min(latencies):.1f} ms")

    # --- Matriz de confusão ---
    cm = confusion_matrix(all_labels, all_preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASS_NAMES)

    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title("Matriz de Confusão - Postura Canina", fontsize=14)
    plt.tight_layout()

    # Salvar figura
    output_path = os.path.join(MODELS_DIR, "confusion_matrix.png")
    os.makedirs(MODELS_DIR, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"\nMatriz de confusão salva em: {output_path}")

    print("\n" + "=" * 60)
    print("AVALIAÇÃO CONCLUÍDA")
    print("=" * 60)

    return {
        "accuracy": accuracy,
        "avg_latency_ms": np.mean(latencies),
        "classification_report": classification_report(
            all_labels, all_preds, target_names=CLASS_NAMES, output_dict=True
        ),
    }


if __name__ == "__main__":
    evaluate()
