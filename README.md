# 🧠 Second Brain AI

A full-stack AI application that acts as your personal knowledge base. Upload PDFs and chat with them using Google Gemini & Vector Search.

### 🚀 Live Demo
**[Click here to try the App](https://second-brain-ai-j55w.onrender.com/)**
*(Note: It runs on a free instance, so please allow 50 seconds for the backend to wake up!)*

---

### 🛠️ Tech Stack
* **Frontend:** React, Vite, TailwindCSS
* **Backend:** FastAPI, Python
* **AI:** LangChain, Google Gemini, ChromaDB (Vector Store)
* **Deployment:** Render (Dockerized)


## How to Run Locally
1. Backend:
   cd backend
   pip install -r requirements.txt
   python main.py
2. Frontend:
   cd frontend
   npm install
   npm run dev
3. Create a .env file in backend with `GOOGLE_API_KEY=...`


## Deployment Options

### Option 1: Manual (Recommended for Testing)
This project uses a Local-First architecture (ChromaDB + Local Embeddings) for privacy and speed.
1. `cd backend && python main.py`
2. `cd frontend && npm run dev`

### Option 2: Docker (Scalable)
The project includes a full Docker configuration (`docker-compose.yml`) for containerized deployment with Redis and PostgreSQL.
* Note: Requires a stable high-bandwidth connection for the initial build.
* Run with: `docker-compose up --build`