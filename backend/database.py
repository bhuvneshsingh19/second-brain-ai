import os
import sys
import shutil
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# --- 1. LINUX/RENDER SQLITE FIX ---
if os.getenv('RENDER') or sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        print("✅ Linux/Render detected: Swapped SQLite to pysqlite3")
    except ImportError:
        print("⚠️ Linux detected but pysqlite3 not found. Using default.")

load_dotenv()

# --- 2. SMART PATH CONFIGURATION ---
# Check if running on Render explicitly
if os.getenv('RENDER'):
    PERSIST_DIRECTORY = "/tmp/chroma_storage"
    print(f"📂 RUNNING ON RENDER: Using temp DB at {PERSIST_DIRECTORY}")
else:
    PERSIST_DIRECTORY = "./chroma_storage"
    print(f"💻 RUNNING LOCALLY: Using local DB at {PERSIST_DIRECTORY}")

# Ensure the directory exists
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

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
        print(f"✅ Successfully saved chunk to {PERSIST_DIRECTORY}")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        raise e

def search_documents(query_text, limit=5):
    results = vector_db.similarity_search_with_score(query_text, k=limit)
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "score": score} 
        for doc, score in results
    ]