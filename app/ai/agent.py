import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.database import get_mysql_engine

load_dotenv()

def get_ai_agent():
    """
    Set up the LangChain agent with Gemini 2.0 Flash and SQL database toolkit.
    """
    # Load Gemini API key
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    # Set up Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_api_key,
        temperature=0.2,
        max_output_tokens=2048
    )

    # Set up SQL database
    engine = get_mysql_engine()
    db = SQLDatabase(engine)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create the agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True
    )
    return agent
