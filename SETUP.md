# 🚀 Guia de Setup - TCC Dog Posture

Passo a passo para rodar o projeto na sua máquina.

---

## 📋 Pré-requisitos

Antes de começar, instale:

1. **Python 3.10+** → [python.org/downloads](https://www.python.org/downloads/)
2. **Node.js 18+** → [nodejs.org](https://nodejs.org/)
3. **Git** → [git-scm.com](https://git-scm.com/)

Para verificar se está tudo instalado, abra o terminal e rode:

```bash
python --version    # deve mostrar 3.10 ou superior
node --version      # deve mostrar 18 ou superior
npm --version       # deve mostrar 9 ou superior
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

# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor
uvicorn main:app --reload --port 8000
```

Se tudo deu certo, acesse: **http://localhost:8000/health**

Você deve ver:
```json
{
  "status": "online",
  "model_loaded": true,
  "model_type": "stub (simulado)"
}
```

---

## 3️⃣ Configurar o Frontend (React)

Abra **outro terminal** (mantenha o backend rodando):

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Rodar o servidor de desenvolvimento
npm run dev
```

Acesse: **http://localhost:5173**

---

## 4️⃣ Testar o MVP

1. Abra http://localhost:5173 no navegador
2. Verifique se o badge mostra "Servidor Online" (verde)
3. Clique em **Iniciar**
4. Permita o acesso à webcam
5. Você verá predições simuladas (stub) aparecendo em tempo real

---

## 🐳 Alternativa: Docker Compose

Se preferir usar Docker:

```bash
# Na raiz do projeto
docker-compose up --build
```

Backend: http://localhost:8000
Frontend: http://localhost:5173

---

## 🔧 Problemas comuns

| Problema | Solução |
|----------|---------|
| "Servidor Offline" no frontend | Verifique se o backend está rodando na porta 8000 |
| Webcam não abre | Verifique permissões do navegador (cadeado na barra de URL) |
| Erro ao instalar dependências Python | Certifique-se de estar no ambiente virtual (venv) |
| `npm run dev` falha | Delete `node_modules` e rode `npm install` novamente |
