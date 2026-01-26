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

# --- CRITICAL: 'app' must be defined globally here, NOT inside a function ---
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
    """Reads text from the specific data files requested."""
    # Logic to find the 'data' folder relative to 'api'
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
                    logger.info(f"✅ Loaded file: {file_path}")
            except Exception as e:
                logger.error(f"❌ Error reading {file_path}: {e}")
        else:
            logger.warning(f"⚠️ File not found: {file_path}")
            
    if not combined_text:
        return "No source data found."
    return combined_text

# Load data immediately
SOURCE_TEXT = load_data()

# Global storage for Index
VECTOR_INDEX = []
CHUNKS = []

class ChatRequest(BaseModel):
    message: str

# ==========================================
#  RAG FUNCTIONS
# ==========================================

def get_embedding(text, client):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def build_index(client):
    global VECTOR_INDEX, CHUNKS
    if CHUNKS: return # Already built

    logger.info("🔨 Building Vector Index...")
    # Simple chunking by period
    raw_chunks = [c.strip() for c in SOURCE_TEXT.replace('\n', ' ').split('.') if len(c.strip()) > 20]
    
    # Limit to 200 chunks to prevent timeouts
    for chunk in raw_chunks[:200]: 
        try:
            vector = get_embedding(chunk, client)
            VECTOR_INDEX.append(vector)
            CHUNKS.append(chunk)
        except Exception:
            pass
    logger.info(f"✅ Indexed {len(CHUNKS)} chunks.")

def retrieve(query, client, top_k=3):
    if not VECTOR_INDEX: return []
    query_vector = get_embedding(query, client)
    scores = [(cosine_similarity(query_vector, vec), chunk) for vec, chunk in zip(VECTOR_INDEX, CHUNKS)]
    scores.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scores[:top_k]]

# ==========================================
#  API ENDPOINTS
# ==========================================

@app.get("/")
def root():
    return {"status": "ok", "rag_enabled": True}

@app.post("/api/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key missing")

    try:
        client = OpenAI(api_key=api_key)
        
        # Build index on first request
        if not CHUNKS:
            build_index(client)

        retrieved_context = retrieve(request.message, client)
        context_str = "\n".join(retrieved_context)
        
        system_prompt = f"Use this context to answer:\n{context_str}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ]
        )
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))