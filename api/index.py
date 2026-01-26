from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import numpy as np
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================================
#  TASK 1: DATA LOADING (From Files)
# ==========================================

def load_data():
    """
    Reads text from the specific data files requested.
    """
    # 1. Define the files we want to read
    # Note: specific relative path logic to find 'data' from 'api' folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [
        os.path.join(base_dir, "data", "HealthWellnessGuide.txt"),
        os.path.join(base_dir, "data", "PMarcaBlogs.txt")
    ]
    
    combined_text = ""
    
    for file_path in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_text += content + "\n\n"
                    logger.info(f"✅ Loaded file: {file_path} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"❌ Error reading {file_path}: {e}")
        else:
            logger.warning(f"⚠️ File not found: {file_path}")
            
    if not combined_text:
        logger.warning("⚠️ No data loaded! RAG will be empty.")
        return "No source data found. Please add data/HealthWellnessGuide.txt."
        
    return combined_text

# Load the data immediately into memory
SOURCE_TEXT = load_data()

# Global storage for our Vector Index (In-Memory)
VECTOR_INDEX = []
CHUNKS = []

class ChatRequest(BaseModel):
    message: str

# ==========================================
#  HELPER FUNCTIONS (Tasks 2-5)
# ==========================================

def get_embedding(text, client):
    """Task 3: Generate Embedding using OpenAI"""
    text = text.replace("\n", " ")
    # Using a smaller model is faster/cheaper, but verify your account has access
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def cosine_similarity(a, b):
    """Task 5: Cosine Similarity Math"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def build_index(client):
    """Tasks 2 & 4: Chunking and Indexing"""
    global VECTOR_INDEX, CHUNKS
    
    # Check if already indexed (Warm Start Optimization)
    if CHUNKS and len(CHUNKS) > 0: 
        logger.info("⚡ Using cached vector index")
        return

    logger.info("🔨 Building Vector Index...")
    
    # TASK 2: Chunking 
    # Simple split by periods. For better results with blogs, 
    # you might want to split by paragraphs ("\n\n") first.
    raw_chunks = [c.strip() for c in SOURCE_TEXT.replace('\n', ' ').split('.') if len(c.strip()) > 20]
    
    temp_index = []
    temp_chunks = []

    # Limit chunks to avoid timeouts on free tier if files are huge
    # Remove [:100] if you have a paid plan and want full indexing
    for chunk in raw_chunks[:200]: 
        try:
            vector = get_embedding(chunk, client)
            temp_index.append(vector)
            temp_chunks.append(chunk)
        except Exception as e:
            logger.error(f"Error embedding chunk: {e}")

    VECTOR_INDEX = temp_index
    CHUNKS = temp_chunks
    
    logger.info(f"✅ Indexed {len(CHUNKS)} chunks.")

def retrieve(query, client, top_k=3):
    """Task 5: Retrieval"""
    if not VECTOR_INDEX:
        return ["No index available."]

    query_vector = get_embedding(query, client)
    
    scores = []
    for i, chunk_vector in enumerate(VECTOR_INDEX):
        score = cosine_similarity(query_vector, chunk_vector)
        scores.append((score, CHUNKS[i]))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    
    # Return top K text chunks
    return [item[1] for item in scores[:top_k]]

# ==========================================
#  API ENDPOINTS
# ==========================================

@app.get("/")
def root():
    return {"status": "ok", "rag_enabled": True, "data_source": "Health & Blogs"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key missing")

    try:
        client = OpenAI(api_key=api_key)
        
        # Build index if empty
        if not CHUNKS:
            build_index(client)

        logger.info(f"🔍 Retrieving context for: {request.message}")
        retrieved_context = retrieve(request.message, client)
        context_str = "\n".join(retrieved_context)
        
        system_prompt = f"""
        You are a helpful assistant. Use the following context to answer the user's question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context_str}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ]
        )
        
        return {
            "reply": response.choices[0].message.content,
            "context_used": retrieved_context 
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))