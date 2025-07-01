from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db, engine
from app.api.auth import get_current_user
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
import app.models.models as models

router = APIRouter()

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

try:
    db_langchain = SQLDatabase(
        engine,
        include_tables=['users', 'skills', 'proficiency_levels', 'project_roles', 'user_skills', 'courses', 'learning_paths', 'user_course_progress'],
        sample_rows_in_table_info=3,
        custom_table_info={
            "users": "Contains employee personal and role information (id, sso_id, first_name, last_name, email, role, current_project_role_id).",
            "skills": "Lists all available skills (id, name, description).",
            "proficiency_levels": "Defines different levels of skill mastery (id, name, description).",
            "user_skills": "Maps employees to their skills and proficiency levels (user_id, skill_id, proficiency_level_id).",
            "project_roles": "Lists defined project roles (id, name, description).",
            "courses": "Contains details about learning courses (id, name, description, skill_id, recommended_proficiency_level_id).",
            "learning_paths": "Defines curated sequences of courses.",
            "user_course_progress": "Tracks individual user progress in courses (user_id, course_id, status, progress_percentage)."
        }
    )
    print("LangChain SQLDatabase initialized successfully within FastAPI.")
except Exception as e:
    print(f"Error initializing LangChain SQLDatabase in chatbot.py: {e}")
    db_langchain = None

llm_chatbot = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

if db_langchain:
    toolkit_chatbot = SQLDatabaseToolkit(db=db_langchain, llm=llm_chatbot)
    agent_executor_chatbot = create_sql_agent(
        llm=llm_chatbot,
        toolkit=toolkit_chatbot,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True
    )
    print("LangChain SQL Agent initialized successfully within FastAPI.")
else:
    agent_executor_chatbot = None
    print("LangChain SQL Agent not initialized due to DB error. Chatbot API may not function.")

@router.post("/query/", response_model=ChatResponse)
async def query_chatbot(
    chat_query: ChatQuery,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not agent_executor_chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service is not initialized. Database connection might be down."
        )
    try:
        if not chat_query.query or not chat_query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        response_text = agent_executor_chatbot.run(chat_query.query)
        return ChatResponse(answer=response_text)
    except Exception as e:
        print(f"Error during chatbot query processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )
