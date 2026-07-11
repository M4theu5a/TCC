<div align="center">

# 🐶 Dog Posture Recognition

**Reconhecimento de Postura de Cães em Tempo Real com Visão Computacional**

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=flat-square&logo=react)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=flat-square)
![TCC](https://img.shields.io/badge/TCC-Engenharia%20de%20Computação-purple?style=flat-square)

> Trabalho de Conclusão de Curso — Engenharia de Computação

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Objetivos](#-objetivos)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Como Executar](#-como-executar)
- [MVP e Roadmap](#-mvp-e-roadmap)
- [Métricas de Avaliação](#-métricas-de-avaliação)
- [Autores](#-autores)

---

## 🐾 Sobre o Projeto

Aplicação web com Inteligência Artificial capaz de reconhecer, **em tempo real**, a postura de cães a partir da webcam, classificando-os em três categorias:

| Postura | Descrição |
|--------|-----------|
| 🟢 Em Pé | Cão erguido sobre as quatro patas |
| 🟡 Sentado | Cão com os quartos traseiros apoiados no chão |
| 🔵 Deitado | Cão com o corpo inteiro sobre o chão |

O sistema utiliza **Transfer Learning** com redes neurais convolucionais (CNN) para classificação das posturas, com inferência via API REST e visualização no navegador em tempo real.

---

## 🎯 Objetivos

### Objetivo Geral

Desenvolver e avaliar uma aplicação web capaz de reconhecer posturas de cães em tempo real utilizando técnicas de Visão Computacional e Aprendizado de Máquina.

### Objetivos Específicos

- [x] Capturar imagens via webcam em tempo real
- [ ] Detectar a presença do cão no frame
- [x] Classificar a postura em três classes (Em Pé, Sentado, Deitado)
- [x] Medir desempenho com acurácia, F1-score, latência e FPS
- [ ] Avaliar robustez em diferentes condições de iluminação e fundo

---

## 🏗 Arquitetura

### Fluxo Geral

```
Webcam (React)
      │
      ▼
Captura de Frame (Canvas)
      │
      ▼
POST /predict  ──────────►  FastAPI (Backend)
                                   │
                                   ▼
                         Pipeline de Inferência (IA)
                         ┌─────────────────────────┐
                         │  1. Pré-processamento    │
                         │  2. Detecção do cão      │
                         │  3. Classificação        │
                         └─────────────────────────┘
                                   │
      ◄────────────────────────────┘
Resposta JSON
{label, confidence, latency_ms}
      │
      ▼
Overlay no Frontend (React)
```

### Formato da Resposta

```json
{
  "label": "SENTADO",
  "confidence": 0.92,
  "latency_ms": 87
}
```

### Componentes

#### 🖥 Frontend — React
- Acesso à webcam via `getUserMedia`
- Extração de frames com `<canvas>`
- Envio dos frames para a API (~5 FPS)
- Exibição da postura, confiança, latência e FPS em overlay

#### ⚙ Backend — FastAPI

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | `GET` | Status da aplicação |
| `/predict` | `POST` | Recebe frame e retorna classificação |

#### 🤖 Pipeline de IA

```
Imagem  →  Pré-processamento  →  Detecção do Cão  →  Classificação  →  Resposta
            (resize, norm.)        (opcional)           (CNN + TL)
```

---

## 🛠 Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React, JavaScript, Canvas API |
| Backend | Python 3.10, FastAPI, Uvicorn |
| IA / ML | CNN, Transfer Learning, OpenCV |
| Infraestrutura | Docker, Docker Compose |

---

## 📂 Estrutura de Pastas

```
tcc-dog-posture/
│
├── backend/
│   ├── main.py                       # Entrypoint FastAPI
│   ├── services/
│   │   ├── inference_service.py      # Orquestra pré-processamento + inferência
│   │   ├── model_arch.py             # Arquitetura do modelo (compartilhada com o treino)
│   │   └── preprocessing.py          # Transforms (compartilhados com o treino)
│   ├── training/                     # Pipeline offline de treino/avaliação
│   │   ├── dataset.py
│   │   ├── train.py
│   │   └── evaluate.py
│   ├── models/                       # Pesos do modelo treinado (.pth, git-ignored)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── services/        # Chamadas à API
│   │   └── App.jsx
│   └── package.json
│
├── docs/
│   ├── diagramas/
│   └── tcc/                 # Documentação acadêmica
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- Bun
- Webcam disponível

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

Abra o navegador em `http://localhost:5173` e **permita o acesso à webcam**.

### Com Docker (recomendado)

```bash
docker-compose up --build
```

### Retreinar o modelo

O checkpoint treinado (`backend/models/dog_posture_model.pth`) não é
versionado no Git (arquivo pesado). Para gerá-lo localmente:

```bash
cd backend
pip install -r requirements.txt -r training/requirements.txt
python training/train.py      # baixa o dataset e treina (leva alguns minutos em CPU)
python training/evaluate.py   # avalia no conjunto de teste e gera métricas
```

Sem o checkpoint, o backend cai automaticamente para um modo stub
(predição simulada) — o `/health` indica isso via `model_type`.

---

## 🗺 MVP e Roadmap

### ✅ MVP — Entrega Inicial

- Captura de webcam funcional
- Envio de frames (~5 FPS, configurável) para a API
- Exibição de: classe, confiança, latência e FPS

### ✅ Modelo Real

- Modelo treinado (MobileNetV2 + Transfer Learning) sobre o dataset
  público [DogPoseCV](https://huggingface.co/datasets/stockeh/dog-pose-cv)
  — ver [`docs/tcc/metodologia.md`](docs/tcc/metodologia.md) e
  [`docs/tcc/resultados.md`](docs/tcc/resultados.md)
- Fallback automático para stub caso o checkpoint não esteja disponível

### 🔄 Próximas Iterações

- [ ] Detector de cão no frame (pré-filtro, hoje o app assume que o
      frame contém um cão)
- [ ] Suavização temporal das predições
- [ ] Otimização de FPS e latência
- [ ] Deploy em produção

---

## 📊 Métricas de Avaliação

Resultado real do modelo treinado (MobileNetV2 + Transfer Learning),
medido no conjunto de teste held-out (1.350 imagens). Detalhes completos,
matriz de confusão e análise em [`docs/tcc/resultados.md`](docs/tcc/resultados.md).

| Métrica | Meta | Resultado real | Status |
|---------|------|-----------------|--------|
| Acurácia | ≥ 80% em ambiente controlado | 71,41% | ❌ |
| F1-score | Avaliado por classe | 71,49% (macro) | ✅ |
| Latência média | < 150 ms por frame | 19,3 ms | ✅ |
| FPS efetivo | ≥ 5 FPS | 51,9 FPS | ✅ |
| Confiança média | ≥ 80% | 70,46% | ❌ |

A acurácia e a confiança média ficaram abaixo da meta original — os
números não foram ajustados para parecer melhores. As hipóteses para essa
diferença (backbone congelada, ambiguidade de rótulos, poucas épocas,
ausência de detector de presença do cão) estão discutidas em
[`docs/tcc/resultados.md`](docs/tcc/resultados.md#análise-e-hipóteses-para-a-diferença-em-relação-à-meta).

Ainda não avaliados nesta rodada: curvas de Precisão/Recall e análise de
robustez em diferentes condições de iluminação e fundo (roadmap).

---

## 📚 Natureza Acadêmica

Este projeto é desenvolvido como Trabalho de Conclusão de Curso em **Engenharia de Computação**, com caráter aplicado, experimental e baseado em evidências quantitativas. A metodologia adota divisão de dados em **treino / validação / teste** e segue práticas de engenharia de software para garantir reprodutibilidade.

---

## 👨‍💻 Autores

<table>
  <tr>
    <td align="center"><b>Matheus</b><br/>Engenharia de Computação</td>
    <td align="center"><b>Kauê</b><br/>Engenharia de Computação</td>
  </tr>
</table>

---

<div align="center">
  <sub>Desenvolvido como TCC — Engenharia de Computação</sub>
</div>