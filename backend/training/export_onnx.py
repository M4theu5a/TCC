"""
Exporta o modelo PyTorch para formato ONNX para inferência otimizada.

Uso:
    cd c:\\Tcc\\backend
    python -m training.export_onnx
"""
import os

import torch

from config import CLASSIFIER_WEIGHTS, CLASSIFIER_ONNX, IMAGE_SIZE, MODELS_DIR
from inference.classifier import create_model


def export_to_onnx():
    """Exporta o modelo treinado para ONNX."""
    print("=" * 60)
    print("EXPORTAÇÃO ONNX")
    print("=" * 60)

    if not os.path.exists(CLASSIFIER_WEIGHTS):
        print(f"ERRO: Modelo não encontrado em {CLASSIFIER_WEIGHTS}")
        print("Execute primeiro: python -m training.train")
        return

    # Carregar modelo
    device = torch.device("cpu")  # ONNX export funciona melhor em CPU
    model = create_model()
    model.load_state_dict(torch.load(CLASSIFIER_WEIGHTS, map_location=device))
    model.eval()

    # Input dummy para tracing
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)

    # Exportar
    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.onnx.export(
        model,
        dummy_input,
        CLASSIFIER_ONNX,
        export_params=True,
        opset_version=13,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        },
    )

    print(f"Modelo ONNX salvo em: {CLASSIFIER_ONNX}")

    # Validar exportação
    _validate_onnx(model, dummy_input)

    file_size_mb = os.path.getsize(CLASSIFIER_ONNX) / (1024 * 1024)
    print(f"Tamanho do arquivo: {file_size_mb:.1f} MB")
    print("=" * 60)
    print("EXPORTAÇÃO CONCLUÍDA")
    print("=" * 60)


def _validate_onnx(model, dummy_input):
    """Verifica se o modelo ONNX produz os mesmos resultados que o PyTorch."""
    import numpy as np
    import onnxruntime as ort

    # Predição PyTorch
    with torch.no_grad():
        pytorch_output = model(dummy_input).numpy()

    # Predição ONNX
    session = ort.InferenceSession(CLASSIFIER_ONNX)
    input_name = session.get_inputs()[0].name
    onnx_output = session.run(None, {input_name: dummy_input.numpy()})[0]

    # Comparar
    diff = np.abs(pytorch_output - onnx_output).max()
    print(f"\nValidação ONNX:")
    print(f"  Diferença máxima (PyTorch vs ONNX): {diff:.6f}")

    if diff < 1e-4:
        print("  ✓ Exportação válida! Resultados consistentes.")
    else:
        print("  ⚠ ATENÇÃO: Diferença acima do esperado.")


if __name__ == "__main__":
    export_to_onnx()
