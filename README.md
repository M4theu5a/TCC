

🐶 TCC – qual o nome???

Trabalho de Conclusão de Curso (TCC) – Engenharia de Computação

Este projeto propõe o desenvolvimento de uma aplicação web com Inteligência Artificial capaz de reconhecer, em tempo real, a postura de cães a partir da webcam, classificando-os em três categorias:

🐾 Em Pé

🐾 Sentado

🐾 Deitado

A aplicação utiliza React (Frontend) e FastAPI (Backend), com modelo de visão computacional implementado em Python.

📌 1. Objetivo do Projeto
🎯 Objetivo Geral

Desenvolver e avaliar uma aplicação web capaz de reconhecer posturas de cães em tempo real utilizando técnicas de Visão Computacional e Aprendizado de Máquina.

📍 Objetivos Específicos

Capturar imagens via webcam em tempo real

Detectar a presença do cão no frame

Classificar a postura em três classes (Em Pé, Sentado, Deitado)

Medir desempenho através de métricas como acurácia, F1-score, latência e FPS

Avaliar robustez em diferentes condições de iluminação e fundo

🧠 2. Fundamentação Técnica

O sistema é baseado em:

Visão Computacional

Redes Neurais Convolucionais (CNN)

Transfer Learning

Processamento de imagens em tempo real

Inferência otimizada para ambiente web

O projeto segue metodologia experimental com divisão de dados em treino, validação e teste.

🏗️ 3. Arquitetura do Sistema
🔄 Fluxo Geral
Webcam (React)
        ↓
Captura de Frame
        ↓
Envio para API (FastAPI)
        ↓
Serviço de Inferência (Modelo IA)
        ↓
Classificação da Postura
        ↓
Retorno JSON (label + confidence + latency)
        ↓
Overlay no Frontend
🧩 Componentes
🖥 Frontend – React

Responsável por:

Captura da webcam (getUserMedia)

Extração de frames via canvas

Envio para API

Exibição da postura e confiança

Exibição de latência e FPS

⚙ Backend – FastAPI

Responsável por:

Receber frames

Executar inferência

Retornar classificação e métricas

Monitoramento de latência

Endpoints principais:

GET  /health
POST /predict
🤖 Serviço de IA

Pipeline de inferência:

Receber imagem

Pré-processamento (resize, normalização)

(Opcional) Detecção do cão

Classificação da postura

Retorno da previsão com confiança

Formato de resposta:

{
  "label": "SENTADO",
  "confidence": 0.92,
  "latency_ms": 87
}
📂 4. Estrutura do Projeto
tcc-dog-posture/
│
├── backend/
│   ├── main.py
│   ├── inference.py
│   ├── models/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── docs/
│   ├── diagramas/
│   └── tcc/
│
├── docker-compose.yml
└── README.md
🚀 5. MVP (Minimum Viable Product)

O MVP entrega:

Captura de webcam

Envio de frames (~5 FPS)

API funcional

Predição simulada (stub)

Exibição de:

Classe prevista

Confiança

Latência

Tempo de resposta total

Próximas evoluções:

Implementar modelo real treinado

Adicionar detector de cães

Suavização temporal das predições

Otimização para melhor FPS

📊 6. Métricas de Avaliação

O projeto será avaliado com base em:

✔ Acurácia

✔ Precisão

✔ Recall

✔ F1-score

✔ Matriz de confusão

✔ Latência média (ms)

✔ FPS efetivo

Meta técnica:

Latência < 150 ms por frame

FPS ≥ 5 FPS

Confiança média ≥ 80% em ambiente controlado

🛠 7. Como Executar
Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
Frontend
cd frontend
npm install
npm run dev

Abrir o navegador e permitir acesso à webcam.

📈 8. Resultados Esperados

Classificação funcional em tempo real

Sistema responsivo

Pipeline modular

Arquitetura escalável

Documentação acadêmica completa

📚 9. Natureza Acadêmica

Este projeto é desenvolvido como Trabalho de Conclusão de Curso em Engenharia de Computação, com caráter:

Aplicado

Experimental

Tecnológico

Baseado em evidências quantitativas

👨‍💻 Autores

Matheus
Kauê
