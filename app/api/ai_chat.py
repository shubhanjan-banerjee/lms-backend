from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.agent import get_ai_agent
from app.ai.agent_memory import AgentWithMemory, get_db_schema
from sqlalchemy import inspect
from app.core.database import get_mysql_engine
from app.core.logger import get_logger
from langchain_google_genai import ChatGoogleGenerativeAI
import os

router = APIRouter(prefix="/ai", tags=["AI Chat"])

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# Global agent and memory context
agent_instance = None
llm_instance = None
agent_memory_instance = None
logger = get_logger(__name__)

def setup_agent_and_check_db():
    global agent_instance, llm_instance, agent_memory_instance
    # Set up agent and LLM
    try:
        agent_instance = get_ai_agent()
        llm_instance = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
            max_output_tokens=2048
        )
        # Check DB access
        engine = get_mysql_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            logger.warning("No tables found in the database! Continuing without raising exception.")
        else:
            logger.info(f"Database tables accessible: {tables}")
        # Set up memory context
        db_schema = get_db_schema()
        agent_memory_instance = AgentWithMemory(agent_instance, llm_instance, db_schema)
        logger.info("Agent and memory context initialized.")
    except Exception as e:
        logger.error(f"Database connection/setup failed: {e}")
        agent_instance = None
        llm_instance = None
        agent_memory_instance = None

# Call setup on module load
setup_agent_and_check_db()

def get_agent_with_memory():
    global agent_memory_instance
    return agent_memory_instance

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest):
    agent_mem = get_agent_with_memory()
    try:
        response = agent_mem.run(request.question)
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
