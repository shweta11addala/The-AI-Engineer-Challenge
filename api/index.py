from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- CRITICAL: 'app' must be defined globally here ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    # 1. Check for API Key inside the function
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not found in environment variables")
        raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing")

    # 2. Initialize Client HERE (Lazy Loading)
    try:
        client = OpenAI(api_key=api_key)
        
        logger.info(f"🚀 Calling OpenAI with message: {request.message[:20]}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": request.message}
            ]
        )
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        logger.error(f"Error calling OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless function handler
def handler(event, context):
    """
    Vercel serverless function handler.
    Wraps Mangum adapter to handle ASGI requests.
    """
    from mangum import Mangum
    mangum_app = Mangum(app, lifespan="off")
    return mangum_app(event, context)