"""
Download e preparação do dataset stockeh/dog-pose-cv (Hugging Face).

A biblioteca `datasets` do Hugging Face depende do pyarrow, que está
bloqueado neste ambiente por uma política de Application Control do
Windows (DLL load failed: "An Application Control policy has blocked this
file"). Por isso este módulo ignora a lib `datasets` e trabalha
diretamente com os tarballs brutos do repositório
(`data/images.tar.gz`, `data/labels.tar.gz`), baixados via
`huggingface_hub` e lidos com `tarfile`/`csv` da biblioteca padrão.

Estrutura dos tarballs (inspecionada manualmente):
- images.tar.gz: images/<synset-breed>/<synset_id>.jpg (+ arquivos
  AppleDouble "._*" que são ignorados)
- labels.tar.gz: labels/<synset-breed>.csv com colunas `id,label`, onde
  label é um de: standing, sitting, lying, undefined
"""

import csv
import random
import sys
import tarfile
from collections import defaultdict
from pathlib import Path

from PIL import Image
from huggingface_hub import hf_hub_download
from torch.utils.data import Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.inference_service import CLASSES  # noqa: E402
from services.preprocessing import build_eval_transform, build_train_transform  # noqa: E402

REPO_ID = "stockeh/dog-pose-cv"
DATA_DIR = Path(__file__).resolve().parent / "data"
IMAGES_DIR = DATA_DIR / "images"
LABELS_DIR = DATA_DIR / "labels"

# Rótulo original do dataset -> classe canônica do projeto (services/inference_service.CLASSES)
HF_TO_CLASS = {
    "standing": "EM_PE",
    "sitting": "SENTADO",
    "lying": "DEITADO",
    # "undefined" é descartado deliberadamente: pose indistinguível/ambígua
}

CAP_PER_CLASS = 3000
SEED = 42
SPLIT_RATIOS = (0.70, 0.15, 0.15)  # train / val / test


def _extract_filtered(tar_path: Path, dest: Path, suffix_filter) -> None:
    """Extrai só os arquivos relevantes do tar, pulando lixo AppleDouble (._*)."""
    with tarfile.open(tar_path) as tf:
        members = [
            m for m in tf.getmembers()
            if m.isfile()
            and not Path(m.name).name.startswith("._")
            and Path(m.name).name.lower().endswith(suffix_filter)
        ]
        tf.extractall(dest, members=members, filter="data")


def _download_and_extract() -> tuple[Path, Path]:
    images_tar = hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename="data/images.tar.gz")
    labels_tar = hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename="data/labels.tar.gz")

    if not IMAGES_DIR.exists():
        print("Extraindo imagens (pode levar alguns minutos)...")
        _extract_filtered(Path(images_tar), DATA_DIR, (".jpg", ".jpeg"))
    if not LABELS_DIR.exists():
        _extract_filtered(Path(labels_tar), DATA_DIR, (".csv",))

    return IMAGES_DIR, LABELS_DIR


def _build_image_index(images_dir: Path) -> dict:
    """Mapeia nome de arquivo -> caminho completo (nomes são únicos: prefixo synset + número)."""
    index = {}
    for path in images_dir.rglob("*.jp*g"):
        index[path.name] = path
    return index


def _load_labeled_samples(labels_dir: Path, image_index: dict) -> list:
    """Lê todos os CSVs de rótulo e retorna [(caminho_imagem, classe_canonica), ...], sem 'undefined'."""
    samples = []
    for csv_path in sorted(labels_dir.rglob("*.csv")):
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                hf_label = row["label"].strip()
                class_name = HF_TO_CLASS.get(hf_label)
                if class_name is None:
                    continue
                image_path = image_index.get(row["id"])
                if image_path is None:
                    continue
                samples.append((image_path, class_name))
    return samples


def _balance_by_class(samples: list, cap: int, seed: int) -> dict:
    """Agrupa por classe e trunca cada classe em `cap` imagens (embaralhadas)."""
    by_class = defaultdict(list)
    for path, class_name in samples:
        by_class[class_name].append(path)

    rng = random.Random(seed)
    balanced = {}
    for class_name in CLASSES:
        paths = by_class[class_name][:]
        rng.shuffle(paths)
        balanced[class_name] = paths[:cap]
    return balanced


def _split_train_val_test(balanced_by_class: dict, ratios: tuple, seed: int) -> tuple:
    """Split estratificado: aplica os mesmos ratios dentro de cada classe."""
    train_ratio, val_ratio, _ = ratios
    rng = random.Random(seed)
    train, val, test = [], [], []

    for class_name, paths in balanced_by_class.items():
        n = len(paths)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train += [(p, class_name) for p in paths[:n_train]]
        val += [(p, class_name) for p in paths[n_train:n_train + n_val]]
        test += [(p, class_name) for p in paths[n_train + n_val:]]

    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)
    return train, val, test


class PostureTorchDataset(Dataset):
    """Dataset PyTorch que lê imagens JPEG do disco e aplica o transform do split."""

    def __init__(self, samples: list, transform):
        self._samples = samples
        self._transform = transform

    def __len__(self):
        return len(self._samples)

    def __getitem__(self, idx):
        path, class_name = self._samples[idx]
        image = Image.open(path).convert("RGB")
        label_idx = CLASSES.index(class_name)
        return self._transform(image), label_idx


def load_splits() -> tuple:
    """Baixa (se necessário), filtra, balanceia e divide o dataset.

    Retorna (train_ds, val_ds, test_ds) como PostureTorchDataset.
    """
    images_dir, labels_dir = _download_and_extract()
    image_index = _build_image_index(images_dir)
    samples = _load_labeled_samples(labels_dir, image_index)

    by_class = _balance_by_class(samples, CAP_PER_CLASS, SEED)
    for class_name in CLASSES:
        print(f"  {class_name}: {len(by_class[class_name])} imagens (após balanceamento)")

    train_samples, val_samples, test_samples = _split_train_val_test(by_class, SPLIT_RATIOS, SEED)
    print(f"Split: treino={len(train_samples)} val={len(val_samples)} teste={len(test_samples)}")

    train_ds = PostureTorchDataset(train_samples, build_train_transform())
    val_ds = PostureTorchDataset(val_samples, build_eval_transform())
    test_ds = PostureTorchDataset(test_samples, build_eval_transform())
    return train_ds, val_ds, test_ds


if __name__ == "__main__":
    load_splits()
