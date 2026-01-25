from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt
import asyncio
import nest_asyncio
import logging

nest_asyncio.apply()
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RAG Prompt Templates
RAG_SYSTEM_TEMPLATE = """You are a helpful personal wellness assistant that answers health and wellness questions based strictly on provided context.

Instructions:
- Only answer questions using information from the provided context
- If the context doesn't contain relevant information, respond with "I don't have information about that in my wellness knowledge base"
- Be accurate and cite specific parts of the context when possible
- Keep responses {response_style} and {response_length}
- Only use the provided context. Do not use external knowledge.
- Include a gentle reminder that users should consult healthcare professionals for medical advice when appropriate
- Only provide answers when you are confident the context supports your response."""

RAG_USER_TEMPLATE = """Context Information:
{context}

Number of relevant sources found: {context_count}
{similarity_scores}

Question: {user_query}

Please provide your answer based solely on the context above."""

# Initialize prompts
rag_system_prompt = SystemRolePrompt(
    RAG_SYSTEM_TEMPLATE,
    strict=True,
    defaults={
        "response_style": "concise",
        "response_length": "brief"
    }
)

rag_user_prompt = UserRolePrompt(
    RAG_USER_TEMPLATE,
    strict=True,
    defaults={
        "context_count": "",
        "similarity_scores": ""
    }
)


class RetrievalAugmentedQAPipeline:
    def __init__(self, llm: ChatOpenAI, vector_db_retriever: VectorDatabase, 
                 response_style: str = "detailed", include_scores: bool = False) -> None:
        self.llm = llm
        self.vector_db_retriever = vector_db_retriever
        self.response_style = response_style
        self.include_scores = include_scores

    def run_pipeline(self, user_query: str, k: int = 4, **system_kwargs) -> dict:
        # Retrieve relevant contexts
        context_list = self.vector_db_retriever.search_by_text(user_query, k=k)
        
        context_prompt = ""
        similarity_scores = []
        
        for i, (context, score) in enumerate(context_list, 1):
            context_prompt += f"[Source {i}]: {context}\n\n"
            similarity_scores.append(f"Source {i}: {score:.3f}")
        
        # Create system message with parameters
        system_params = {
            "response_style": self.response_style,
            "response_length": system_kwargs.get("response_length", "detailed")
        }
        
        formatted_system_prompt = rag_system_prompt.create_message(**system_params)
        
        user_params = {
            "user_query": user_query,
            "context": context_prompt.strip(),
            "context_count": len(context_list),
            "similarity_scores": f"Relevance scores: {', '.join(similarity_scores)}" if self.include_scores else ""
        }
        
        formatted_user_prompt = rag_user_prompt.create_message(**user_params)

        return {
            "response": self.llm.run([formatted_system_prompt, formatted_user_prompt]), 
            "context": context_list,
            "context_count": len(context_list),
            "similarity_scores": similarity_scores if self.include_scores else None,
            "prompts_used": {
                "system": formatted_system_prompt,
                "user": formatted_user_prompt
            }
        }


# Initialize FastAPI app
app = FastAPI()

# CORS so the frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize vector database and RAG pipeline (lazy initialization)
vector_db = None
rag_pipeline = None

def initialize_rag_pipeline():
    """Initialize the RAG pipeline with vector database"""
    global vector_db, rag_pipeline
    
    if vector_db is not None and rag_pipeline is not None:
        return  # Already initialized
    
    try:
        # Check if data file exists
        data_file = "data/HealthWellnessGuide.txt"
        if not os.path.exists(data_file):
            logger.warning(f"Data file {data_file} not found. RAG features will not be available.")
            return
        
        # Load and process documents
        logger.info("Loading documents for RAG pipeline...")
        text_loader = TextFileLoader(data_file)
        documents = text_loader.load_documents()
        
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_texts(documents)  # Fixed: split_texts not split_documents
        
        # Initialize embedding model and vector database
        embedding_model = EmbeddingModel(embeddings_model_name="text-embedding-3-small")
        vector_db = VectorDatabase(embedding_model=embedding_model)
        vector_db = asyncio.run(vector_db.abuild_from_list(chunks))
        
        # Initialize chat model and RAG pipeline
        chat_openai = ChatOpenAI(model_name="gpt-4.1-mini")
        rag_pipeline = RetrievalAugmentedQAPipeline(
            vector_db_retriever=vector_db,
            llm=chat_openai,
            response_style="detailed",
            include_scores=True
        )
        
        logger.info("RAG pipeline initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        logger.info("Falling back to standard chat mode")


class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    logger.info(f"📥 Received chat request: {request.message[:50]}...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not configured")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    logger.info(f"✅ API key found (length: {len(api_key)}, starts with: {api_key[:7]}...)")
    
    # Initialize RAG pipeline if not already done
    initialize_rag_pipeline()
    
    try:
        user_message = request.message
        
        # Use RAG pipeline if available, otherwise fall back to standard chat
        if rag_pipeline is not None:
            logger.info("🚀 Using RAG pipeline for response")
            response = rag_pipeline.run_pipeline(
                user_message,
                k=3,
                response_length="comprehensive"
            )
            reply = response["response"]  # Fixed: access dict key, not response object
            logger.info(f"✅ RAG pipeline call successful! Response length: {len(reply)}")
        else:
            # Fallback to standard chat
            logger.info("🚀 Using standard chat mode (RAG not available)")
            model_name = "gpt-3.5-turbo"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a supportive mental coach, you always answer in a supportive and encouraging tone."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content
            logger.info(f"✅ OpenAI API call successful! Response length: {len(reply)}")
        
        return {"reply": reply}
    
    except Exception as e:
        error_str = str(e)
        logger.error(f"❌ Error: {error_str}")
        
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
