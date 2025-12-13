import os
import time
from celery import Celery
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import insert_document, get_embedding
import json

celery = Celery(__name__, broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"))

@celery.task
def process_file_task(file_path, file_type, original_filename):
    print(f"Processing {file_type}: {original_filename}")
    
    # 1. Load Data
    docs = []
    try:
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        elif file_type == "web":
            loader = WebBaseLoader(file_path)
            docs = loader.load()
        elif file_type == "text":
            from langchain_core.documents import Document
            with open(file_path, 'r') as f:
                text = f.read()
            docs = [Document(page_content=text)]
    except Exception as e:
        print(f"Error loading file: {e}")
        return "Failed to load file"

    # 2. Chunk Data
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"Total chunks to process: {len(splits)}")

    # 3. Embed & Store (Bulletproof Retry Logic)
    success_count = 0
    
    for i, split in enumerate(splits):
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Attempt to embed
                vector = get_embedding(split.page_content)
                
                metadata = json.dumps({
                    "source": original_filename,
                    "type": file_type,
                    "page": split.metadata.get("page", 0)
                })
                insert_document(split.page_content, metadata, vector)
                
                success_count += 1
                print(f"Processed chunk {i+1}/{len(splits)}")
                
                # Success! Break the retry loop and move to next chunk
                # Sleep 5s to be nice to the API
                time.sleep(5)
                break 

            except Exception as e:
                attempt += 1
                print(f"Error on chunk {i+1} (Attempt {attempt}/{max_retries}): {e}")
                
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("HIT RATE LIMIT. Sleeping for 30 seconds to cool down...")
                    time.sleep(30) # Long wait to escape penalty box
                else:
                    print("Generic error, waiting 5 seconds...")
                    time.sleep(5)
        
        if attempt == max_retries:
            print(f"FAILED to process chunk {i+1} after {max_retries} attempts. Skipping.")

    # Cleanup temp file
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return f"Indexed {success_count}/{len(splits)} chunks from {original_filename}"