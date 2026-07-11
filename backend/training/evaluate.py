"""
Avaliação do modelo treinado no split de teste (held-out).

Gera:
- backend/models/metrics.json          (consumido pelo endpoint GET /metrics)
- docs/tcc/resultados/confusion_matrix.png
- docs/tcc/resultados/classification_report.txt

Uso: a partir de backend/
    python training/evaluate.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.inference_service import CLASSES  # noqa: E402
from services.model_arch import build_model  # noqa: E402
from dataset import load_splits  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BACKEND_DIR / "models" / "dog_posture_model.pth"
METRICS_JSON_PATH = BACKEND_DIR / "models" / "metrics.json"
RESULTS_DIR = BACKEND_DIR.parent / "docs" / "tcc" / "resultados"


def _load_model(device) -> torch.nn.Module:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Checkpoint nao encontrado em {MODEL_PATH}. Rode 'python training/train.py' primeiro."
        )
    model = build_model(num_classes=len(CLASSES), pretrained=False, freeze_backbone=False)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()
    return model


def _collect_predictions(model, loader, device):
    all_labels, all_preds = [], []
    latencies_ms = []

    with torch.no_grad():
        for images, labels in loader:
            for i in range(images.size(0)):
                single = images[i:i + 1].to(device)
                start = time.perf_counter()
                output = model(single)
                latencies_ms.append((time.perf_counter() - start) * 1000)
                pred = output.argmax(dim=1).item()
                all_preds.append(pred)
                all_labels.append(labels[i].item())

    return all_labels, all_preds, latencies_ms


def main():
    device = torch.device("cpu")
    model = _load_model(device)

    print("Carregando dataset (split de teste)...")
    _train_ds, _val_ds, test_ds = load_splits()
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=4)

    print(f"Avaliando em {len(test_ds)} imagens de teste...")
    y_true, y_pred, latencies_ms = _collect_predictions(model, test_loader, device)

    report_dict = classification_report(y_true, y_pred, target_names=CLASSES, output_dict=True, zero_division=0)
    report_text = classification_report(y_true, y_pred, target_names=CLASSES, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    accuracy = report_dict["accuracy"]
    mean_latency_ms = sum(latencies_ms) / len(latencies_ms)
    effective_fps = 1000.0 / mean_latency_ms if mean_latency_ms > 0 else 0.0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASSES)
    fig, ax = plt.subplots(figsize=(6, 6))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Matriz de Confusao - Teste (held-out)")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    (RESULTS_DIR / "classification_report.txt").write_text(report_text, encoding="utf-8")

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "classes": CLASSES,
        "test_set_size": len(test_ds),
        "accuracy": accuracy,
        "per_class": {
            cls: {
                "precision": report_dict[cls]["precision"],
                "recall": report_dict[cls]["recall"],
                "f1_score": report_dict[cls]["f1-score"],
                "support": report_dict[cls]["support"],
            }
            for cls in CLASSES
        },
        "macro_avg_f1": report_dict["macro avg"]["f1-score"],
        "confusion_matrix": cm.tolist(),
        "mean_latency_ms": mean_latency_ms,
        "effective_fps": effective_fps,
    }
    METRICS_JSON_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(report_text)
    print(f"Acuracia: {accuracy:.4f} | Latencia media: {mean_latency_ms:.1f}ms | FPS efetivo: {effective_fps:.1f}")
    print(f"\nArtefatos salvos em:\n  {METRICS_JSON_PATH}\n  {RESULTS_DIR / 'confusion_matrix.png'}\n  {RESULTS_DIR / 'classification_report.txt'}")


if __name__ == "__main__":
    main()
