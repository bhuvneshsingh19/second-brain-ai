# --- 1. LINUX/RENDER SQLITE FIX (MUST BE AT THE VERY TOP) ---
import sys
import os

# We must apply this fix BEFORE importing anything else (like langchain or chroma)
if os.getenv('RENDER') or sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        print("✅ Linux/Render detected: Swapped SQLite to pysqlite3")
    except ImportError:
        print("⚠️ Linux detected but pysqlite3 not found. Using default.")
# ------------------------------------------------------------

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- 2. SMART CONFIGURATION ---
# On Render, we use None (Memory-Only) to strictly avoid disk permission errors.
# On Laptop, we use disk storage so you can restart without losing data.
if os.getenv('RENDER'):
    PERSIST_DIRECTORY = None 
    print("🧠 RUNNING ON RENDER: Using In-Memory Database (No Disk)")
else:
    PERSIST_DIRECTORY = "./chroma_storage"
    print(f"💻 RUNNING LOCALLY: Using disk DB at {PERSIST_DIRECTORY}")

# 3. Initialize Embeddings
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing!")

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=api_key
)

# 4. Initialize ChromaDB
vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings_model,
    collection_name="second_brain_files"
)

def insert_document(content, meta):
    try:
        vector_db.add_texts(texts=[content], metadatas=[meta])
        print("✅ Chunk saved successfully.")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        raise e

def search_documents(query_text, limit=5):
    results = vector_db.similarity_search_with_score(query_text, k=limit)
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "score": score} 
        for doc, score in results
    ]