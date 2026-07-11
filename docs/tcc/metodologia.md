# Metodologia

## 1. Dataset

O modelo foi treinado com o dataset **DogPoseCV** ([`stockeh/dog-pose-cv`](https://huggingface.co/datasets/stockeh/dog-pose-cv),
Hugging Face, licença Apache 2.0), curado por Jason Stock e Tom Cavey
(Colorado State University) a partir do
[Stanford Dogs Dataset](http://vision.stanford.edu/aditya86/ImageNetDogs/),
com as imagens re-rotuladas por postura.

Distribuição original (20.578 imagens, 120 raças):

| Classe original | Imagens |
|---|---|
| `lying` (deitado) | 7.090 |
| `undefined` (indistinguível) | 6.307 |
| `standing` (em pé) | 4.143 |
| `sitting` (sentado) | 3.038 |

### 1.1 Filtragem e balanceamento

- A classe `undefined` foi **descartada** — o dataset original a utiliza
  para poses ambíguas ou indistinguíveis (em geral retratos em close-up),
  que não correspondem a nenhuma das três classes-alvo do projeto.
- As classes restantes foram mapeadas para o vocabulário do projeto:
  `standing → EM_PE`, `sitting → SENTADO`, `lying → DEITADO`.
- Para mitigar o desbalanceamento (deitado tem ~2,3x mais imagens que
  sentado), cada classe foi limitada (*cap*) a **3.000 imagens**,
  selecionadas aleatoriamente (seed fixa = 42). Como a classe minoritária
  (`sitting`, 3.038 imagens) está logo acima do cap, o corte usa
  praticamente toda a classe minoritária disponível, resultando em um
  dataset final balanceado de **9.000 imagens** (3.000 por classe).

### 1.2 Divisão treino / validação / teste

Divisão estratificada por classe, na proporção **70% / 15% / 15%**:

| Split | Imagens | Por classe |
|---|---|---|
| Treino | 6.300 | 2.100 |
| Validação | 1.350 | 450 |
| Teste (held-out) | 1.350 | 450 |

O conjunto de teste não é usado em nenhuma etapa do treino ou da seleção
de hiperparâmetros — é reservado exclusivamente para a avaliação final
reportada em [`resultados.md`](resultados.md).

## 2. Pré-processamento e augmentação

Todas as imagens são redimensionadas para **224×224** (entrada padrão de
redes pré-treinadas na ImageNet) e normalizadas com média/desvio-padrão da
ImageNet (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).

No conjunto de treino, é aplicada augmentação de dados para melhorar a
generalização e reduzir overfitting na camada classificadora:
- Espelhamento horizontal aleatório
- Rotação aleatória (±15°)
- Jitter de cor (brilho, contraste e saturação, ±20%)

Validação e teste usam apenas resize + normalização (sem augmentação), e
o **mesmo transform é reutilizado na inferência em produção**
(`backend/services/preprocessing.py`), eliminando divergência entre o
pré-processamento de treino/avaliação e o que roda de fato na API.

## 3. Arquitetura e Transfer Learning

- **Backbone:** MobileNetV2, pré-treinada na ImageNet
  (`torchvision.models.mobilenet_v2`, pesos `MobileNet_V2_Weights.DEFAULT`).
- **Congelamento:** os pesos do extrator de características (`features`)
  ficam congelados durante o treino — apenas a camada classificadora final
  é treinada. Essa é a abordagem clássica de Transfer Learning para
  datasets pequenos/médios: reaproveita as características visuais
  genéricas aprendidas na ImageNet (bordas, texturas, formas) e adapta
  apenas a decisão final para o problema de 3 classes.
- **Camada de saída:** `nn.Linear(last_channel, 3)`, substituindo a
  camada original de 1000 classes da ImageNet.

## 4. Hiperparâmetros de treino

| Hiperparâmetro | Valor |
|---|---|
| Otimizador | Adam |
| Taxa de aprendizado | 1e-3 |
| Função de perda | Cross-Entropy |
| Batch size | 32 |
| Épocas | 12 |
| Seed | 42 |
| Hardware | CPU (sem GPU disponível no ambiente de desenvolvimento) |

Não foram usados pesos de classe na função de perda porque o dataset já
foi balanceado na etapa de preparação (Seção 1.1).

O checkpoint salvo é o de **melhor acurácia de validação** entre as 12
épocas (early best-checkpoint, não necessariamente a última época).

## 5. Avaliação

A avaliação final roda exclusivamente sobre o conjunto de teste
(held-out, nunca visto durante o treino), medindo:
- Acurácia geral
- Precisão, recall e F1-score por classe (`sklearn.metrics.classification_report`)
- Matriz de confusão
- Latência média de inferência por imagem (medida com o mesmo caminho de
  código usado em produção, `services/inference_service.py::_predict_real`)

Os resultados obtidos estão documentados em [`resultados.md`](resultados.md).

## 6. Reprodutibilidade

Todo o pipeline é versionado em `backend/training/`:

```bash
cd backend
pip install -r requirements.txt -r training/requirements.txt
python training/train.py      # baixa o dataset, treina e salva o checkpoint
python training/evaluate.py   # avalia no teste e gera métricas/matriz de confusão
```

O dataset é baixado automaticamente do Hugging Face na primeira execução
(cache local, não versionado no Git — ver `.gitignore`).

### Nota técnica

A biblioteca `datasets` do Hugging Face (que normalmente seria o caminho
padrão para carregar datasets do Hub) depende do `pyarrow`, cuja DLL
nativa está bloqueada neste ambiente de desenvolvimento por uma política
de *Application Control* do Windows. Por isso, `backend/training/dataset.py`
baixa e lê diretamente os tarballs brutos do repositório do dataset
(`data/images.tar.gz`, `data/labels.tar.gz`) via `huggingface_hub` e as
bibliotecas padrão `tarfile`/`csv`, sem depender do `pyarrow`.
