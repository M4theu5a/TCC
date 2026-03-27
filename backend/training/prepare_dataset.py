"""
Script para preparação do dataset de postura canina.
Baixa imagens de cães usando URLs públicas e organiza em pastas por classe.

INSTRUÇÕES:
    1. Crie manualmente as pastas com imagens, OU
    2. Execute este script para criar a estrutura e orientações.

Estrutura esperada:
    backend/dataset/
        DEITADO/    (cão deitado)
        EM_PE/      (cão em pé)
        SENTADO/    (cão sentado)

Uso:
    cd c:\\Tcc\\backend
    python -m training.prepare_dataset
"""
import os
import sys

from config import DATASET_DIR, CLASS_NAMES


def create_dataset_structure():
    """Cria a estrutura de diretórios do dataset."""
    print("=" * 60)
    print("PREPARAÇÃO DO DATASET")
    print("=" * 60)

    for class_name in CLASS_NAMES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
        print(f"  ✓ Criado: {class_dir}")

    print(f"\nEstrutura criada em: {DATASET_DIR}")
    print()
    print("PRÓXIMOS PASSOS:")
    print("-" * 60)
    print()
    print("Adicione imagens de cães nas pastas correspondentes:")
    print()
    print(f"  {os.path.join(DATASET_DIR, 'DEITADO')}\\")
    print("    → Imagens de cães DEITADOS")
    print()
    print(f"  {os.path.join(DATASET_DIR, 'EM_PE')}\\")
    print("    → Imagens de cães EM PÉ")
    print()
    print(f"  {os.path.join(DATASET_DIR, 'SENTADO')}\\")
    print("    → Imagens de cães SENTADOS")
    print()
    print("RECOMENDAÇÕES:")
    print("  • Mínimo 100 imagens por classe (ideal: 300+)")
    print("  • Formatos aceitos: .jpg, .jpeg, .png")
    print("  • Variedade de raças, ângulos e iluminação")
    print("  • Imagens com fundo variado (não apenas estúdio)")
    print()
    print("FONTES DE IMAGENS:")
    print("  • Google Images (buscar 'dog standing', 'dog sitting', 'dog lying down')")
    print("  • Kaggle: Stanford Dogs Dataset")
    print("  • Open Images Dataset (Google)")
    print("  • Tirar fotos próprias (recomendado para TCC)")
    print()
    print("Após adicionar as imagens, execute o treinamento:")
    print("  cd c:\\Tcc\\backend")
    print("  python -m training.train")
    print("=" * 60)

    # Verificar se já existem imagens
    total_images = 0
    for class_name in CLASS_NAMES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        if os.path.exists(class_dir):
            images = [
                f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))
            ]
            count = len(images)
            total_images += count
            status = "✓" if count >= 100 else "⚠" if count > 0 else "✗"
            print(f"  {status} {class_name}: {count} imagens")

    if total_images == 0:
        print("\n  Nenhuma imagem encontrada. Adicione imagens nas pastas acima.")
    elif total_images < 300:
        print(f"\n  Total: {total_images} imagens (recomendado: 300+ no total)")
    else:
        print(f"\n  Total: {total_images} imagens ✓")
        print("  Dataset pronto para treinamento!")


if __name__ == "__main__":
    create_dataset_structure()
