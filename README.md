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
- [ ] Classificar a postura em três classes (Em Pé, Sentado, Deitado)
- [ ] Medir desempenho com acurácia, F1-score, latência e FPS
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
│   ├── main.py              # Entrypoint FastAPI
│   ├── inference.py         # Pipeline de inferência
│   ├── models/              # Pesos do modelo treinado
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
- Node.js 18+
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
npm install
npm run dev
```

Abra o navegador em `http://localhost:5173` e **permita o acesso à webcam**.

### Com Docker (recomendado)

```bash
docker-compose up --build
```

---

## 🗺 MVP e Roadmap

### ✅ MVP — Entrega Inicial

- Captura de webcam funcional
- Envio de frames (~5 FPS) para a API
- API com predição stub (simulada)
- Exibição de: classe, confiança, latência e FPS

### 🔄 Próximas Iterações

- [ ] Modelo real treinado com dataset de cães
- [ ] Detector de cão no frame (pré-filtro)
- [ ] Suavização temporal das predições
- [ ] Otimização de FPS e latência
- [ ] Deploy em produção

---

## 📊 Métricas de Avaliação

O projeto será avaliado com as seguintes métricas:

| Métrica | Meta |
|---------|------|
| Acurácia | ≥ 80% em ambiente controlado |
| F1-score | Avaliado por classe |
| Latência média | < 150 ms por frame |
| FPS efetivo | ≥ 5 FPS |
| Confiança média | ≥ 80% |

Além disso, serão geradas: **matriz de confusão**, curvas de **Precisão/Recall** e análise de robustez em diferentes condições de iluminação e fundo.

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