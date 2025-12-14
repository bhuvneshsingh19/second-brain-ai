from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import shutil
import os
import sys
import uvicorn

# Import database functions from your database.py file
from database import insert_document, search_documents

# --- LOAD ENV VARIABLES ---
from dotenv import load_dotenv
load_dotenv()
# --------------------------

app = FastAPI()

# --- SMART STARTUP CLEANUP ---
# This matches the logic in database.py to ensure we clean the right folder.
if os.getenv('RENDER'):
    DB_PATH = "/tmp/chroma_storage"
    print("🚀 Startup: Detected RENDER environment.")
else:
    DB_PATH = "./chroma_storage"
    print("💻 Startup: Detected LOCAL environment.")

print(f"🧹 Checking for old database at {DB_PATH}...")
if os.path.exists(DB_PATH):
    try:
        shutil.rmtree(DB_PATH)
        print(f"✅ Cleaned up old database at {DB_PATH}")
    except Exception as e:
        print(f"⚠️ Could not clear DB (might be in use or permission error): {e}")
else:
    print("ℹ️ No old database found. Starting fresh.")
# -----------------------------

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
    # Create a temp folder for processing the raw PDF
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file.filename}"
    
    # Save the uploaded file temporarily
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
        
        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = splitter.split_documents(docs)

        # Insert chunks into the database
        # (database.py handles saving to the correct /tmp/ folder automatically)
        for split in splits:
            meta = {"source": file.filename, "type": type}
            insert_document(split.page_content, meta)
        
        print(f"Success! Indexed {len(splits)} chunks.")
        return {"message": "File processed and indexed successfully"}
        
    except Exception as e:
        print(f"❌ Error in upload: {e}")
        return {"message": f"Error processing file: {str(e)}"}
    finally:
        # Always clean up the raw uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. Search Local DB
    try:
        results = search_documents(request.message)
    except Exception as e:
        print(f"❌ Database Search Error: {e}")
        return {"reply": "I cannot access my memory right now. Please try uploading the document again.", "sources": []}
    
    context_text = ""
    if results:
        context_text = "\n\n".join([r["content"] for r in results])
    
    # 2. Generate Answer with Google Gemini
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"reply": "System Error: API Key missing.", "sources": []}

    # Use the robust model alias we found earlier
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest", 
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