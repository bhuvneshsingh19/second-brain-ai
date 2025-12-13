import os
import shutil
# CHANGED: Switch from HuggingFace (Heavy) to Google (Lightweight)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# --- LOAD ENV VARIABLES ---
from dotenv import load_dotenv
load_dotenv()
# --------------------------

# 1. Initialize Google Embeddings (Zero RAM usage on server)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing!")

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # Standard Google Model
    google_api_key=api_key
)

# 2. Initialize ChromaDB
# We ensure the DB directory exists
PERSIST_DIRECTORY = "./chroma_db"

vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings_model,
    collection_name="second_brain_files"
)

def insert_document(content, meta):
    vector_db.add_texts(texts=[content], metadatas=[meta])

def search_documents(query_text, limit=5):
    results = vector_db.similarity_search_with_score(query_text, k=limit)
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "score": score} 
        for doc, score in results
    ]