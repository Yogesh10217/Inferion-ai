# 🚀 Inferion AI — Complete Scratch Setup & Execution Guide

This step-by-step guide walks you through setting up and running **Inferion AI** (FastAPI Core Gateway & Next.js Control Plane Dashboard) from complete scratch on Windows, macOS, or Linux.

---

## 📌 Prerequisites

Make sure you have the following installed on your computer:
* **Python**: `3.10` or higher (`python --version`)
* **Node.js**: `18.0` or higher (`node -v` & `npm -v`)
* **Git**: Installed (`git --version`)
* *(Optional)* **Docker & Docker Compose**: For containerized deployment (`docker --version`)

---

## 🚀 Method 1: Local Setup from Scratch (Recommended for Dev)

### Step 1: Open Terminal & Navigate to Project Directory
```powershell
# Open terminal or PowerShell and navigate to repository root
cd "c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"
```

---

### Step 2: Set Up Python Virtual Environment
```powershell
# Create Python virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On macOS / Linux:
# source .venv/bin/activate
```

---

### Step 3: Install Python Dependencies
```powershell
# Upgrade pip and install required backend packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)
Create or verify the `.env` file in the root directory:

```env
# Application Settings
APP_NAME="Inferion AI"
ENVIRONMENT="development"
HOST="0.0.0.0"
PORT=8002

# Optional OpenAI Integration (Pasting your OpenAI key allows live OpenAI model calls)
OPENAI_API_KEY="sk-proj-your-openai-key-here"

# Security & Local Dev Authorization Settings
AUTH_ENABLED=true
ALLOW_ANONYMOUS=true
JWT_SECRET="super-secret-jwt-token-key"
```

---

### Step 5: Start the FastAPI Backend Gateway
In your backend terminal window:

```powershell
# Start FastAPI backend engine on port 8002
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```
> 🩺 **FastAPI API Swagger Docs**: Open [http://localhost:8002/docs](http://localhost:8002/docs)  
> 🌐 **Health Check**: Open [http://localhost:8002/health](http://localhost:8002/health)

---

### Step 6: Install & Start the Next.js Web Control Plane Dashboard
Open a **second terminal window** and navigate to `frontend/`:

```powershell
# Navigate to frontend folder
cd frontend

# Install Node.js frontend dependencies
npm install

# Start Next.js development server
npm run dev
```

> 🎨 **Enterprise Web Control Plane Dashboard**: Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

---

## 🐳 Method 2: One-Command Docker Compose Setup

If you have Docker Desktop installed, you can spin up the full stack (FastAPI Backend + Next.js Control Plane + Redis + PostgreSQL + Prometheus) with one command:

```powershell
# Build and run all services in containerized mode
docker compose up -d --build
```

### Stop Docker Stack:
```powershell
docker compose down
```

---

## 🧭 How to Use the Application Features

| Feature | URL | How to Use |
|---|---|---|
| **💬 Chat / Inference Playground** | [http://localhost:3000/dashboard](http://localhost:3000/dashboard) | Click **"Inference Console"**, type a question (e.g. *"What is the capital of Japan?"*), and click **Run Inference Call**. |
| **➕ Register / Add Models (UI)** | [http://localhost:3000/dashboard/routing](http://localhost:3000/dashboard/routing) | Click **"+ Register New Model"** to add custom LLMs visually via modal. |
| **🗑️ Delete Models (UI)** | [http://localhost:3000/dashboard/routing](http://localhost:3000/dashboard/routing) | Click the **Trash (`🗑️`) icon** next to any model row to unregister it. |
| **💰 FinOps Cost & Savings** | [http://localhost:3000/dashboard/finops](http://localhost:3000/dashboard/finops) | View real-time cost tracking, token consumption, and model savings. |
| **🔑 API Keys & Permissions** | [http://localhost:3000/dashboard/keys](http://localhost:3000/dashboard/keys) | Manage API keys, access roles, and tenant quotas. |

---

## 🔌 Connecting Your External AI Applications

Inferion AI is 100% drop-in compatible with the official **OpenAI SDK**. You can connect any external Python/Node.js app by setting `base_url="http://localhost:8002/v1"`:

```python
from openai import OpenAI

# Connect your Python app directly to Inferion AI
client = OpenAI(
    base_url="http://localhost:8002/v1",
    api_key="sk-inferion-test-key"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain machine learning in 1 sentence."}]
)

print(response.choices[0].message.content)
```

---

## 🧪 Verification & Running Tests

To verify full system correctness and run automated test suites:

```powershell
# Run full pytest backend test suite (1,800+ tests)
.venv\Scripts\pytest.exe

# Build production Next.js frontend bundle
cd frontend
npm run build

# Validate Helm Kubernetes deployment manifests
python scripts/validate_helm_k8s.py
```

---

## ❓ Common Troubleshooting & FAQs

* **Q: Why am I getting `401 Unauthorized`?**  
  **A:** Ensure `ALLOW_ANONYMOUS=true` is set in your `.env` file for local development.

* **Q: Why does live OpenAI call return `429 credit_balance_exhausted`?**  
  **A:** Your OpenAI account has $0 balance. Add credits at [OpenAI Billing](https://platform.openai.com/settings/organization/billing). The gateway will automatically fall back to local answers or $0 Ollama models if billing is inactive.

* **Q: Where can I view interactive Swagger API documentation?**  
  **A:** Visit [http://localhost:8002/docs](http://localhost:8002/docs).
