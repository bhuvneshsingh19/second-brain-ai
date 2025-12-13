from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import shutil
import os
import uvicorn
from database import insert_document, search_documents

# --- NEW: LOAD ENV VARIABLES ---
from dotenv import load_dotenv
# Try loading from current folder, or go up one level to root
load_dotenv() 
load_dotenv("../.env") 
# -------------------------------

app = FastAPI()

if os.path.exists("./chroma_db"):
    try:
        shutil.rmtree("./chroma_db")
        print("🧹 Cleaned up old database storage for fresh start.")
    except Exception as e:
        print(f"⚠️ Could not clear DB: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), type: str = Form(...)):
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        print(f"Processing {file.filename}...")
        docs = []
        if type == "pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        elif type == "text":
            with open(file_path, 'r', encoding='utf-8') as f:
                docs = [Document(page_content=f.read())]
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = splitter.split_documents(docs)

        for split in splits:
            meta = {"source": file.filename, "type": type}
            insert_document(split.page_content, meta)
        
        print(f"Success! Indexed {len(splits)} chunks.")
        return {"message": "File processed and indexed successfully"}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"message": f"Error processing file: {str(e)}"}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. Search Local DB
    results = search_documents(request.message)
    
    # Optional: If no results found, you can still answer generally
    context_text = ""
    if results:
        context_text = "\n\n".join([r["content"] for r in results])
    
    # 2. Generate Answer with Google Gemini
    # Ensure Key is grabbed from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("CRITICAL ERROR: GOOGLE_API_KEY is missing from environment.")
        return {"reply": "System Error: API Key missing. Please check .env file.", "sources": []}

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",  # <--- Use this alias from your list
        google_api_key=api_key
    )
    
    messages = [
        SystemMessage(content=f"You are a helpful Second Brain AI. Answer based on this Context:\n\n{context_text}"),
        HumanMessage(content=request.message)
    ]
    
    try:
        response = llm.invoke(messages)
        return {
            "reply": response.content,
            "sources": [r["metadata"]["source"] for r in results]
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"reply": "I'm having trouble thinking right now. (API Error)", "sources": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)