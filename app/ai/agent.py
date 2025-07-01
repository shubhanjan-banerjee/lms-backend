import os
from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.sql import text
from app.core.database import get_mysql_engine

load_dotenv()

def get_ai_agent():
    """
    Set up the LangChain agent with Gemini 2.0 Flash and SQL database toolkit.
    Also checks that engine, db, and toolkit are ready and logs their status.
    """
    import logging
    logger = logging.getLogger("lms-backend.app.ai.agent")
    # Load Gemini API key
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables.")
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    # Set up Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_api_key,
        temperature=0.2,
        max_output_tokens=2048,
        max_retries=2
    )

    # Set up SQL database
    try:
        engine = get_mysql_engine()
        logger.info(f" --------------- SQLAlchemy engine created: {engine}")
        # Test engine connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(" --------------- Engine connection test passed.")
    except Exception as e:
        logger.error(f" --------------- Engine connection failed: {e}")
        raise
    try:
        db = SQLDatabase(engine)
        logger.info(f" --------------- LangChain SQLDatabase created: {db}")
        # Test table access
        tables = db.get_usable_table_names()
        logger.info(f" --------------- Usable tables: {tables}")
    except Exception as e:
        logger.error(f" --------------- SQLDatabase setup failed: {e}")
        raise
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        logger.info(f" --------------- SQLDatabaseToolkit created: {toolkit}")
    except Exception as e:
        logger.error(f" --------------- SQLDatabaseToolkit setup failed: {e}")
        raise

    # Create the agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS, # This agent type is still compatible with Google's function calling models
        handle_parsing_errors=True # Helps recover from potential LLM parsing issues
    )
    logger.info("LangChain SQL agent created and ready.")
    return agent
