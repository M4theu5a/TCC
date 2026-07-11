# 🚀 Guia de Setup - TCC Dog Posture

Passo a passo para rodar o projeto na sua máquina, **com o modelo de IA
real** (não mais o stub simulado). Se você só quer testar a interface sem
esperar o treino, pule direto para a seção 5 — o app funciona igual, só
que com predições aleatórias claramente marcadas como "Modo Stub".

> Quer entender **como** tudo isso funciona por dentro (o que conversa com
> o quê, como o treino funciona)? Leia
> [`docs/tcc/como_funciona.md`](docs/tcc/como_funciona.md).

---

## 📋 Pré-requisitos

Antes de começar, instale:

1. **Python 3.10+** → [python.org/downloads](https://www.python.org/downloads/)
2. **Bun** → [bun.sh](https://bun.sh/) (ou Node.js + npm, se preferir)
3. **Git** → [git-scm.com](https://git-scm.com/)

Para verificar se está tudo instalado, abra o terminal e rode:

```bash
python --version    # deve mostrar 3.10 ou superior
bun --version       # deve mostrar a versão instalada do Bun
git --version       # deve mostrar qualquer versão
```

---

## 1️⃣ Clonar o repositório

```bash
git clone https://github.com/M4theu5a/TCC.git
cd TCC
```

---

## 2️⃣ Configurar o Backend (FastAPI)

```bash
# Entrar na pasta do backend
cd backend

# Criar ambiente virtual (isola as dependências)
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências de produção da API
pip install -r requirements.txt
```

> **Nota:** o `requirements.txt` já inclui `torch`/`torchvision` (usados
> tanto para treinar quanto para rodar o modelo treinado). O download
> desses pacotes pode demorar alguns minutos na primeira vez.

---

## 3️⃣ Treinar o modelo (opcional, mas recomendado)

O repositório **não** inclui o modelo já treinado (o arquivo `.pth` é
pesado demais para o Git — ver `.gitignore`). Sem ele, o backend cai
automaticamente para um modo *stub* (predição aleatória), então o app
funciona de qualquer forma, mas sem inteligência real.

Para treinar o modelo de verdade:

```bash
# ainda dentro de backend/, com o venv ativado
pip install -r training/requirements.txt
python training/train.py
```

O que esse comando faz:
- Baixa automaticamente o dataset público
  [DogPoseCV](https://huggingface.co/datasets/stockeh/dog-pose-cv) do
  Hugging Face (~780MB de imagens — só na primeira execução).
- Treina uma rede MobileNetV2 (Transfer Learning) por 12 épocas.
- Salva o melhor modelo em `backend/models/dog_posture_model.pth`.

⏱ **Tempo esperado:** o treino roda inteiramente em CPU (não precisa de
GPU). Em uma máquina comum, espere de 20 a 60 minutos, dependendo do
processador. O terminal pode ficar sem mostrar nada por vários minutos
seguidos por causa de buffer de saída — isso é normal, o processo está
trabalhando (se quiser confirmar, veja se o uso de CPU está alto).

Depois do treino, gere as métricas de avaliação (usadas na aba
"Métricas" do app):

```bash
python training/evaluate.py
```

Isso cria `backend/models/metrics.json` e, em
`docs/tcc/resultados/`, a matriz de confusão e o relatório de
classificação.

> Detalhes completos da metodologia (dataset, hiperparâmetros, divisão
> treino/validação/teste) estão em
> [`docs/tcc/metodologia.md`](docs/tcc/metodologia.md), e os resultados
> obtidos em [`docs/tcc/resultados.md`](docs/tcc/resultados.md).

### Compartilhando o modelo já treinado (sem precisar retreinar)

O `.gitignore` do projeto exclui `*.pth` por padrão, presumindo que o
arquivo do modelo seria pesado demais para o Git. Na prática, o
checkpoint gerado por este pipeline (MobileNetV2 com a maior parte da
rede congelada) fica em torno de **8-9 MB** — tranquilamente dentro do
limite do GitHub (100 MB por arquivo). Ou seja, **dá para compartilhar
o modelo treinado**, sem cada pessoa da equipe precisar treinar do zero.
Algumas formas de fazer isso:

1. **Commitar o arquivo direto no Git** (mais simples, dado o tamanho
   pequeno): remova a linha `backend/models/*.pth` (e, se quiser, `*.pth`)
   do `.gitignore` e rode `git add backend/models/dog_posture_model.pth`
   normalmente. Quem der `git pull` já recebe o modelo pronto.
2. **Enviar o arquivo diretamente** (Drive, WeTransfer, Discord/WhatsApp
   etc.) para quem for rodar o projeto, que só precisa colocá-lo em
   `backend/models/dog_posture_model.pth` — o backend detecta e carrega
   automaticamente na próxima inicialização.
3. **Publicar como um "Release" do GitHub** (anexando o `.pth` como
   asset do release) — mantém o repositório principal leve e ainda
   versiona os checkpoints.

Independentemente da forma escolhida, `backend/models/metrics.json` (as
métricas de avaliação) **já é versionado no Git** — não está no
`.gitignore` — então os resultados ficam visíveis no repositório mesmo
para quem não tem o arquivo de pesos.

---

## 4️⃣ Rodar o servidor backend

```bash
# ainda dentro de backend/
uvicorn main:app --reload --port 8000
```

Se tudo deu certo, acesse: **http://localhost:8000/health**

Com o modelo treinado (passo 3 concluído), você deve ver:
```json
{
  "status": "online",
  "model_loaded": true,
  "model_type": "modelo_treinado"
}
```

Se pulou o passo 3, `model_type` vai aparecer como `"stub (simulado)"` —
o servidor funciona normalmente, só que sem inteligência real.

---

## 5️⃣ Configurar o Frontend (React)

Abra **outro terminal** (mantenha o backend rodando):

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
bun install

# Rodar o servidor de desenvolvimento
bun run dev
```

Acesse: **http://localhost:5173**

---

## 6️⃣ Testar o sistema

1. Abra http://localhost:5173 no navegador.
2. Verifique se o badge no topo mostra "API Conectada" (e, na barra
   lateral, se "Modelo de IA" mostra "Treinado").
3. Clique em **Iniciar**, na aba Dashboard, e permita o acesso à webcam.
4. Aponte a câmera para um cão (ou uma foto/vídeo de um cão) em pé,
   sentado ou deitado — a predição no card "Predição Atual" e o overlay
   sobre o vídeo devem atualizar em tempo real.
5. Explore as outras abas da barra lateral:
   - **Sobre o Projeto** — visão geral e stack tecnológico.
   - **Métricas** — acurácia, F1 por classe e matriz de confusão do
     modelo treinado (só aparece com dados reais depois do passo 3).
   - **Configurações** — ajuste a taxa de captura (FPS) da webcam.
   - **Documentação** — aponta para os documentos do projeto.

---

## 🐳 Alternativa: Docker Compose

Se preferir usar Docker:

```bash
# Na raiz do projeto
docker-compose up --build
```

Backend: http://localhost:8000
Frontend: http://localhost:5173

> O `docker-compose.yml` monta `./backend` como volume dentro do
> container, então se você já treinou o modelo localmente (passo 3), o
> arquivo `dog_posture_model.pth` já vai estar disponível dentro do
> container automaticamente — não precisa treinar de novo nem alterar o
> Dockerfile.

---

## 🔧 Problemas comuns

| Problema | Solução |
|----------|---------|
| "API Offline" no frontend | Verifique se o backend está rodando na porta 8000 |
| Webcam não abre | Verifique permissões do navegador (cadeado na barra de URL) |
| Erro ao instalar dependências Python | Certifique-se de estar no ambiente virtual (venv) ativado |
| `bun run dev` falha | Delete `node_modules` e rode `bun install` novamente |
| "Modelo de IA: Modo Stub" mesmo após treinar | Confira se `backend/models/dog_posture_model.pth` existe e reinicie o backend (o modelo só é carregado na inicialização) |
| `training/train.py` trava baixando o dataset | Verifique sua conexão — o download é de ~780MB e vem do Hugging Face Hub |
| Erro `ImportError: DLL load failed` ao importar `datasets`/`pyarrow` | Em alguns Windows com política de Application Control, o `pyarrow` é bloqueado. Não é um problema: `training/dataset.py` já contorna isso e não depende da biblioteca `datasets` — se você editou esse arquivo, veja a nota técnica em [`docs/tcc/como_funciona.md`](docs/tcc/como_funciona.md#44-por-que-datasetpy-não-usa-a-biblioteca-datasets-do-hugging-face) |
