from fastapi import FastAPI, HTTPException, Request
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
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        user_message = request.message
        # Using GPT-5.2 - OpenAI's latest model with enhanced capabilities
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": user_message}
            ]
        )
        return {"reply": response.choices[0].message.content}
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

# Vercel serverless function handler (only needed for Vercel deployment)
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # mangum not needed for local development
    handler = None
