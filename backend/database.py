import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load Local Embedding Model (Free, runs on CPU)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Initialize ChromaDB (Saves data to a local folder named 'chroma_db')
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings_model,
    collection_name="second_brain_files"
)

def insert_document(content, meta):
    # Chroma handles the vector conversion automatically!
    vector_db.add_texts(texts=[content], metadatas=[meta])

def search_documents(query_text, limit=5):
    # Retrieve top matches
    results = vector_db.similarity_search_with_score(query_text, k=limit)
    
    # Format output
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "score": score} 
        for doc, score in results
    ]