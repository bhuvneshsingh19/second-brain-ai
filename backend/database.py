import os
import shutil
import sys
from dotenv import load_dotenv

# --- SMART FIX FOR RENDER DEPLOYMENT ---
# This checks: "Am I running on Linux?"
# If yes, it applies the SQLite fix for ChromaDB.
# If no (Windows), it skips this and runs normally.
if sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        pass
# ---------------------------------------

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# 1. Initialize Google Embeddings
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing!")

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=api_key
)

# 2. Initialize ChromaDB
vector_db = Chroma(
    persist_directory="./chroma_db",
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