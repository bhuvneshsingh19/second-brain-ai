# --- SMART DATABASE CONFIGURATION ---
import os
import shutil
import sys
from dotenv import load_dotenv

# 1. Linux/Render Compatibility Fix (SQLite)
if sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        pass

# 2. Define the Brain Storage Location
# On Render (Linux), we MUST use /tmp because the main folder is Read-Only.
# On Windows (Laptop), we use the local folder.
if sys.platform.startswith('linux'):
    PERSIST_DIRECTORY = "/tmp/chroma_db"
else:
    PERSIST_DIRECTORY = "./chroma_db"

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# 3. Initialize Embeddings (Google)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing!")

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=api_key
)

# 4. Initialize ChromaDB at the correct writable path
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