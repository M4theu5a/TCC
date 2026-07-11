"""
Arquitetura do modelo de classificação de postura.

Único ponto de definição da arquitetura, usado tanto pelo treino
(backend/training/) quanto pela inferência em produção
(services/inference_service.py), para garantir que o modelo carregado
em produção seja estruturalmente idêntico ao que foi treinado.
"""

import torch.nn as nn
import torchvision.models as models


def build_model(num_classes: int, pretrained: bool = True, freeze_backbone: bool = True) -> nn.Module:
    """
    Constrói uma MobileNetV2 adaptada para `num_classes` classes.

    Args:
        num_classes: número de classes de saída.
        pretrained: se True, carrega os pesos pré-treinados na ImageNet.
        freeze_backbone: se True, congela os pesos do extrator de
            características (`features`), deixando apenas a camada
            classificadora final treinável (Transfer Learning clássico).
    """
    weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
    model = models.mobilenet_v2(weights=weights)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    model.classifier[1] = nn.Linear(model.last_channel, num_classes)

    return model
