from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS so the frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"📥 Received chat request: {request.message[:50]}...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not configured")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    logger.info(f"✅ API key found (length: {len(api_key)}, starts with: {api_key[:7]}...)")
    
    try:
        user_message = request.message
        # Try gpt-3.5-turbo first (more likely to work on free tier)
        # If you have access to GPT-5.2, you can change this back
        model_name = "gpt-3.5-turbo"
        logger.info(f"🚀 Calling OpenAI API with model: {model_name}")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": user_message}
            ]
        )
        
        reply = response.choices[0].message.content
        logger.info(f"✅ OpenAI API call successful! Response length: {len(reply)}")
        return {"reply": reply}
    except Exception as e:
        error_str = str(e)
        # Check for specific OpenAI error types
        if "insufficient_quota" in error_str or "quota" in error_str.lower():
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API quota exceeded. Please check your OpenAI account billing and usage limits. You may need to add payment information or upgrade your plan."
            )
        elif "401" in error_str or "unauthorized" in error_str.lower() or "Invalid API key" in error_str:
            raise HTTPException(
                status_code=500,
                detail="Invalid OpenAI API key. Please check your API key configuration."
            )
        elif "429" in error_str or "rate limit" in error_str.lower():
            raise HTTPException(
                status_code=500,
                detail="OpenAI API rate limit exceeded. Please wait a moment and try again."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {error_str}")

# Vercel serverless function handler
# Must be at module level for Vercel to detect it
from mangum import Mangum
handler = Mangum(app, lifespan="off")
