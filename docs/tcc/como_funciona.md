# Como Tudo Funciona — Guia Completo

Este documento explica, em detalhe e sem pressupor conhecimento prévio do
código, como as três partes do projeto (frontend, backend e o pipeline de
treino do modelo) conversam entre si e como uma predição acontece do
início ao fim.

---

## 1. Visão geral: as três partes do sistema

```
┌─────────────────┐        HTTP (porta 8000)        ┌──────────────────┐
│   FRONTEND       │ ───────────────────────────────▶ │   BACKEND         │
│  React + Vite     │ ◀─────────────────────────────── │  FastAPI (Python) │
│  (porta 5173)      │         JSON                     │                   │
└─────────────────┘                                    └─────────┬─────────┘
                                                                    │ carrega
                                                                    ▼
                                                       ┌────────────────────┐
                                                       │  MODELO TREINADO    │
                                                       │  dog_posture_model  │
                                                       │  .pth (arquivo)     │
                                                       └────────────────────┘
                                                                    ▲
                                                                    │ gerado por
                                                       ┌────────────────────┐
                                                       │  PIPELINE DE TREINO  │
                                                       │  backend/training/    │
                                                       │  (roda offline, uma   │
                                                       │  vez, separado do app)│
                                                       └────────────────────┘
```

**Frontend** e **backend** são dois processos completamente separados,
rodando em portas diferentes (5173 e 8000), que só se falam por HTTP. O
**pipeline de treino** é uma terceira coisa, ainda mais separada: não roda
junto com o app, é executado manualmente (ou uma vez só) para *produzir um
arquivo* (`dog_posture_model.pth`) que o backend depois lê ao iniciar.

Ou seja: treinar o modelo e rodar o app são duas atividades independentes.
Você treina uma vez (ou sempre que quiser melhorar o modelo), e o arquivo
resultante fica salvo em disco. O app, toda vez que inicia, simplesmente
carrega esse arquivo já pronto — ele não treina nada em tempo real.

---

## 2. O ciclo de vida de uma predição (passo a passo)

Isso é o que acontece, em ordem, quando você aperta "Iniciar" na webcam e
o sistema começa a mostrar predições:

### 2.1 Captura do frame (frontend)

Arquivo: [`frontend/src/components/WebcamCapture.jsx`](../../frontend/src/components/WebcamCapture.jsx)

1. `navigator.mediaDevices.getUserMedia(...)` pede acesso à webcam do
   navegador e conecta o stream de vídeo a uma tag `<video>` (invisível
   para o usuário, só serve de fonte).
2. A cada intervalo de tempo (por padrão a cada 200ms = 5 vezes por
   segundo, configurável na tela "Configurações" do app), a função
   `captureFrame()` desenha o frame atual do vídeo dentro de um
   `<canvas>` (`ctx.drawImage(video, 0, 0)`).
3. O canvas é convertido para uma imagem JPEG em memória
   (`canvas.toBlob(..., 'image/jpeg', 0.8)`) — isso é um `Blob`, os bytes
   crus da imagem, como se fosse um arquivo `.jpg` sem estar salvo em
   disco.
4. Esse Blob é passado para a função `onFrame(blob)`, que é na verdade a
   função `handleFrame` definida em `App.jsx`.

### 2.2 Envio para o backend (frontend → backend)

Arquivo: [`frontend/src/services/api.js`](../../frontend/src/services/api.js)

5. `handleFrame` (em `App.jsx`) chama `predictFrame(blob)`.
6. `predictFrame` monta um `FormData` (o mesmo formato usado por
   formulários HTML com upload de arquivo) e faz um
   `POST http://localhost:8000/predict` usando a biblioteca `axios`.
7. A URL do backend vem de `API_BASE_URL` em `api.js` — por padrão
   `http://localhost:8000`, mas pode ser trocada por uma variável de
   ambiente `VITE_API_URL` (útil se um dia o backend rodar em outro
   endereço, como em produção).

Nesse ponto, a imagem literalmente viajou do navegador para o processo
Python do backend, como um upload de arquivo comum.

### 2.3 Recebimento e roteamento (backend)

Arquivo: [`backend/main.py`](../../backend/main.py)

8. O FastAPI recebe a requisição na rota `@app.post("/predict")`.
9. Lê os bytes do arquivo enviado (`await file.read()`).
10. Repassa esses bytes para `inference_service.predict(image_bytes)` —
    o `inference_service` é uma instância única de `InferenceService`,
    criada uma vez quando o servidor sobe (não é recriada a cada
    requisição).
11. Depois de receber o resultado, `main.py` calcula a latência total
    (tempo desde que a requisição chegou) e devolve um JSON:
    `{"label": "SENTADO", "confidence": 0.92, "latency_ms": 87}`.

### 2.4 A predição de verdade (backend → modelo)

Arquivo: [`backend/services/inference_service.py`](../../backend/services/inference_service.py)

12. `preprocess_image()` abre os bytes recebidos com `PIL.Image` e
    garante que a imagem está em RGB.
13. Como o modelo foi carregado com sucesso na inicialização (mais
    detalhes na seção 3), `predict()` chama `_predict_real(image)`:
    - A imagem passa pelo mesmo `transform` usado no treino/avaliação
      (`services/preprocessing.py::build_eval_transform()`): redimensiona
      para 224×224 e normaliza os valores de pixel com a
      média/desvio-padrão da ImageNet.
    - O tensor resultante entra na rede neural (`self._model(tensor)`),
      que devolve 3 números (um "score" por classe: EM_PE, SENTADO,
      DEITADO).
    - `softmax` transforma esses 3 números em probabilidades que somam
      100% (ex: 5% / 92% / 3%).
    - A classe com maior probabilidade vira o `label`, e a probabilidade
      dela vira o `confidence`.
14. Esse dicionário `{"label": ..., "confidence": ...}` volta para
    `main.py`, que devolve a resposta HTTP para o frontend.

### 2.5 Atualização da tela (backend → frontend)

Arquivo: [`frontend/src/App.jsx`](../../frontend/src/App.jsx)

15. `handleFrame` recebe a resposta, atualiza vários estados do React:
    `prediction`, `latency`, `confidence`, o histórico das últimas 10
    predições, as médias/sparklines do painel de métricas etc.
16. O React re-renderiza a tela automaticamente: o card "Predição Atual"
    mostra o novo label e a barra de confiança, o overlay sobre o vídeo
    mostra o nome da postura detectada, e assim por diante.
17. Isso se repete a cada frame capturado (passo 2.1), enquanto a webcam
    estiver ligada — por isso parece "tempo real", mas na verdade é uma
    sequência rápida de requisições HTTP independentes, uma por frame.

**Resumindo o ciclo inteiro:** webcam → canvas → JPEG → HTTP POST →
FastAPI → pré-processamento → rede neural → softmax → HTTP response →
React atualiza a tela. Isso tudo acontece em ~50-150ms por frame.

---

## 3. Como o backend decide "modelo real" vs "stub"

Isso é importante entender porque o projeto tem os dois modos.

Quando o servidor FastAPI inicia (`uvicorn main:app`), a função
`lifespan()` em `main.py` chama `inference_service.load_model()`. Essa
função (em `inference_service.py`) tenta:

1. Verificar se existe o arquivo `backend/models/dog_posture_model.pth`.
2. Se existir, construir a arquitetura do modelo
   (`services/model_arch.py::build_model()`) e carregar os pesos
   treinados nela (`model.load_state_dict(...)`).
3. Se **tudo der certo**, `self._use_stub = False` — a partir daí, toda
   predição usa a rede neural de verdade.
4. Se **qualquer coisa falhar** (arquivo não existe, arquivo corrompido,
   erro ao carregar), o backend **não trava**: ele cai automaticamente
   para o modo *stub*, que devolve uma classe aleatória (só para o app
   continuar funcionando fim a fim, sem crashar, mesmo sem modelo).

Você consegue ver qual modo está ativo de duas formas:
- Chamando `GET /health` — o campo `model_type` diz
  `"modelo_treinado"` ou `"stub (simulado)"`.
- Olhando a barra lateral do app: o indicador "Modelo de IA" mostra
  "Treinado" (verde) ou "Modo Stub" (vermelho/cinza).

Isso significa que **o app funciona mesmo sem o modelo treinado**
(mostrando predições aleatórias, claramente marcadas como stub), e
**automaticamente passa a usar o modelo de verdade** assim que o arquivo
`.pth` existir — sem precisar mudar nenhuma configuração manualmente.

---

## 4. Como o treino funciona (passo a passo)

O treino é um processo *separado*, que você roda manualmente uma vez
(ou sempre que quiser gerar um modelo novo). Ele não faz parte do
"rodar o app" do dia a dia. Fica todo em `backend/training/`.

### 4.1 `dataset.py` — baixar e preparar os dados

1. Baixa dois arquivos do Hugging Face Hub (repositório público
   `stockeh/dog-pose-cv`): `images.tar.gz` (as fotos, ~780MB) e
   `labels.tar.gz` (arquivos CSV dizendo qual é a postura de cada foto).
2. Extrai esses arquivos para `backend/training/data/` (essa pasta **não**
   é enviada pro Git — é grande demais e pode ser regerada a qualquer
   momento rodando o script de novo).
3. Lê os CSVs de rótulo. Cada linha diz `nome_da_imagem.jpg,postura`,
   onde `postura` é `standing`, `sitting`, `lying` ou `undefined`.
4. Descarta as imagens rotuladas como `undefined` (pose ambígua — não
   interessa pro projeto, que só tem 3 classes).
5. Como uma classe (`lying`/deitado) tem muito mais fotos que as outras,
   o código corta cada classe em no máximo 3.000 imagens, para o dataset
   final ficar balanceado (3.000 + 3.000 + 3.000 = 9.000 imagens).
6. Separa essas 9.000 imagens em 3 grupos, sem misturar:
   - **Treino** (6.300 imagens) — usado para ajustar os pesos da rede.
   - **Validação** (1.350 imagens) — usado durante o treino só para
     checar se o modelo está melhorando, sem nunca ser usado para ajustar
     pesos.
   - **Teste** (1.350 imagens) — fica guardado, intocado, e só é usado
     no final para medir o desempenho real do modelo (a "prova final").

### 4.2 `train.py` — ensinar a rede neural

7. Carrega uma rede **MobileNetV2** já pré-treinada na ImageNet (um
   dataset gigante e genérico com 1000 categorias de objetos do
   dia-a-dia). Essa rede já "sabe" reconhecer formas, texturas e padrões
   visuais básicos.
8. **Congela** a maior parte da rede (ela não muda durante o treino) e
   troca só a última camada por uma nova, com 3 saídas (uma para cada
   postura). Isso se chama **Transfer Learning**: em vez de aprender a
   "ver" do zero (o que exigiria milhões de imagens), a rede só precisa
   aprender a *reaproveitar* o que já sabe ver, para decidir entre 3
   categorias novas.
9. Passa pelas 6.300 imagens de treino, em grupos de 32 (`batch_size`),
   repetindo esse processo 12 vezes (`épocas`). Em cada grupo:
   - a rede tenta prever a postura,
   - compara com a resposta certa (`CrossEntropyLoss`, a "função de
     erro"),
   - ajusta os pesos da última camada para errar um pouco menos da
     próxima vez (`optimizer.step()`).
10. Ao final de cada época, mede a acurácia no grupo de **validação**
    (que a rede nunca usa para ajustar pesos, só para "prestar contas").
    Se essa acurácia for a melhor até agora, salva os pesos atuais em
    `backend/models/dog_posture_model.pth` — assim, mesmo que uma época
    posterior piore (overfitting), o arquivo salvo é sempre o melhor que
    já apareceu.

### 4.3 `evaluate.py` — a prova final

11. Carrega o checkpoint salvo (o melhor modelo) e roda **só uma vez**
    sobre as 1.350 imagens de **teste** — que a rede nunca viu nem para
    treinar nem para validar.
12. Calcula métricas de verdade: acurácia geral, precisão/recall/F1 por
    classe, matriz de confusão (quantas vezes o modelo confundiu
    "sentado" com "deitado", por exemplo), e a latência média por
    imagem.
13. Salva esses números em `backend/models/metrics.json` (que o backend
    expõe pela rota `GET /metrics`, consumida pela tela "Métricas" do
    app) e também salva uma imagem da matriz de confusão + um relatório
    de texto em `docs/tcc/resultados/`.

### 4.4 Por que dataset.py não usa a biblioteca `datasets` do Hugging Face

Detalhe técnico que vale registrar: o jeito "padrão" de baixar datasets do
Hugging Face é a biblioteca `datasets`, mas ela depende de outra
biblioteca (`pyarrow`) cuja DLL está bloqueada nesta máquina por uma
política de segurança do Windows (Application Control). Por isso,
`dataset.py` baixa os arquivos `.tar.gz` brutos do repositório
diretamente (usando `huggingface_hub`, que não depende do `pyarrow`) e os
lê com `tarfile`/`csv`, módulos que já vêm prontos no Python. Funciona
igual, só não passa pela biblioteca de conveniência.

---

## 5. Mapa de arquivos: quem fala com quem

| Arquivo | Papel |
|---|---|
| `frontend/src/components/WebcamCapture.jsx` | Captura frames da webcam |
| `frontend/src/App.jsx` | Estado global da tela, decide o que renderizar |
| `frontend/src/services/api.js` | Único ponto que fala HTTP com o backend |
| `backend/main.py` | Recebe requisições HTTP, define as rotas |
| `backend/services/inference_service.py` | Decide modelo real vs. stub, faz a predição |
| `backend/services/model_arch.py` | Define a arquitetura da rede (usado pelo treino **e** pela inferência — garante que são a mesma rede) |
| `backend/services/preprocessing.py` | Define o pré-processamento da imagem (idem — mesmo código no treino e na inferência) |
| `backend/models/dog_posture_model.pth` | O arquivo com os pesos treinados (gerado pelo treino, lido pela inferência) |
| `backend/models/metrics.json` | Resultado da avaliação (gerado pelo treino, lido pela rota `/metrics`) |
| `backend/training/dataset.py` | Baixa e prepara os dados |
| `backend/training/train.py` | Treina a rede |
| `backend/training/evaluate.py` | Avalia a rede treinada |

`model_arch.py` e `preprocessing.py` ficam em `backend/services/` (não em
`backend/training/`) de propósito: são o "contrato" compartilhado entre
treino e produção. Se o treino usasse uma arquitetura ou um
pré-processamento ligeiramente diferente do que a inferência usa, o
modelo pareceria "burro" mesmo estando bem treinado — os dois lados
importam exatamente as mesmas funções, então não têm como divergir.

---

## 6. Portas, URLs e CORS (por que às vezes dá erro de conexão)

- Backend roda em `http://localhost:8000` (definido em
  `uvicorn main:app --port 8000`).
- Frontend roda em `http://localhost:5173` (definido pelo Vite).
- Como são origens diferentes (portas diferentes), o navegador bloquearia
  a comunicação por padrão (política de CORS). Por isso `main.py`
  configura `CORSMiddleware` liberando explicitamente
  `http://localhost:5173` (e `:3000`, caso o frontend rode em outra
  porta padrão do React).
- Se você mudar a porta do frontend ou hospedar o backend em outro
  endereço, precisa: (1) adicionar a nova origem em `allow_origins` no
  `main.py`, e (2) apontar `VITE_API_URL` (variável de ambiente do
  frontend) para o novo endereço do backend.

---

## 7. Perguntas rápidas

**"Se eu desligar o backend, o que acontece?"**
O frontend continua rodando (é só HTML/JS no navegador), mas o badge de
status vira "API Offline" e o botão "Iniciar" fica desabilitado — o
`checkHealth()` em `api.js` roda a cada 10 segundos para detectar isso.

**"Preciso treinar o modelo toda vez que ligo o projeto?"**
Não. Treinar é uma etapa única (ou ocasional, se quiser melhorar o
modelo). O arquivo `.pth` gerado fica salvo em disco; o backend só lê
esse arquivo pronto sempre que inicia.

**"Como sei se está usando o modelo real ou o stub?"**
`GET /health` → campo `model_type`. Ou visualmente, na barra lateral do
app, indicador "Modelo de IA".

**"Onde ficam os resultados de acurácia/F1/matriz de confusão?"**
Na tela "Métricas" do app (puxa de `GET /metrics`, que lê
`backend/models/metrics.json`), e também documentado em
[`resultados.md`](resultados.md).
