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