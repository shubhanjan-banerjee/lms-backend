import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker # Import sessionmaker if not already imported in your core.database
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

# --- 1. Prerequisites ---
# Ensure you have the following packages installed:
# pip install langchain-community sqlalchemy pymysql google-generativeai

# --- 2. Database Configuration & Engine from your setup ---
# Assuming your app.core.database has 'engine' defined like this:
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.core.config import DATABASE_URL # Assuming your DB URL is here

# DATABASE_URL = "mysql+pymysql://user:password@host:port/dbname" # Example
# engine = create_engine(
#     DATABASE_URL, 
#     pool_pre_ping=True, 
#     connect_args={"auth_plugin": "mysql_native_password"} # IMPORTANT: Include this here if using mysql_native_password
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Re-creating the engine here for demonstration purposes, but in a real app
# you would import 'engine' directly from your 'app.core.database' module.
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "lms_db")

DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the engine using your connect_args, simulating its definition in app.core.database
engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True, # Recommended for long-running applications
    connect_args={"auth_plugin": "mysql_native_password"}
)

# You can optionally define SessionLocal here as well if you need to test sessions directly
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 3. Initialize SQLDatabase for LangChain using the existing 'engine' ---
try:
    # Use from_engine() instead of from_uri()
    db = SQLDatabase(
        engine, # Pass the SQLAlchemy engine directly
        include_tables=['users', 'skills', 'proficiency_levels', 'project_roles', 'user_skills'],
        sample_rows_in_table_info=3,
        custom_table_info={
            "users": "Contains employee personal and role information.", 
            "skills": "Lists all available skills.",
            "proficiency_levels": "Defines different levels of skill mastery.",
            "user_skills": "Maps employees to their skills and proficiency levels.",
            "project_roles": "Lists defined project roles."
        }
    )
    print("Successfully connected to the database!")
except Exception as e:
    print(f"Error initializing SQLDatabase: {e}")
    print("Please ensure MySQL server is running, and the engine is correctly configured.")
    exit()

# --- 4. Initialize the Language Model (LLM) ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# --- 5. Create the SQL Agent ---
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True
)

# --- 6. Interact with the Agent ---
print("\n--- LangChain SQL Agent Ready ---")

try:
    print("\nQuery 1: What is John Doe's email address and current project role?")
    response1 = agent_executor.run("What is John Doe's email address and current project role?")
    print(f"Agent Response: {response1}")

    print("\nQuery 2: List all developers and their assigned project roles.")
    response2 = agent_executor.run("List all developers and their assigned project roles.")
    print(f"Agent Response: {response2}")

    print("\nQuery 3: What skills does Jane Smith have and at what proficiency level?")
    response3 = agent_executor.run("What skills does Jane Smith have and at what proficiency level?")
    print(f"Agent Response: {response3}")

    print("\nQuery 4: Which employees have 'JavaScript' skill at 'Proficient' level or higher? Show their names and proficiency.")
    response4 = agent_executor.run("Which employees have 'JavaScript' skill at 'Proficient' level or higher? Show their names and proficiency.")
    print(f"Agent Response: {response4}")

    print("\nQuery 5: How many employees are 'Frontend Developer'?")
    response5 = agent_executor.run("How many employees are 'Frontend Developer'?")
    print(f"Agent Response: {response5}")

except Exception as e:
    print(f"\nAn error occurred during agent execution: {e}")
    print("Check the 'verbose' output above for detailed trace if available.")
