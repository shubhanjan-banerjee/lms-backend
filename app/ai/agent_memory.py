from langchain.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import PromptTemplate
from app.core.database import get_mysql_engine
from sqlalchemy import inspect

class SimpleSessionHistory:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def format_history(self):
        history = ""
        for msg in self.messages:
            if msg["role"] == "user":
                history += f"Human: {msg['content']}\n"
            elif msg["role"] == "ai":
                history += f"AI: {msg['content']}\n"
        return history.strip()

class AgentWithMemory:
    def __init__(self, agent, llm, db_schema):
        self.agent = agent
        self.llm = llm
        self.db_schema = db_schema
        self.prompt_template = PromptTemplate(
            input_variables=["input", "history"],
            template=(
                "You are an AI assistant with access to the following MySQL database schema:\n"
                "{db_schema}\n"
                "Keep this schema in mind for all answers.\n"
                "\n"
                "{history}\nHuman: {input}\nAI:"
            ).replace("{db_schema}", db_schema)
        )
        self._session_history = SimpleSessionHistory()
        def get_session_history(session_id: str):
            return self._session_history
        self.chain = RunnableWithMessageHistory(
            self.agent,  # Use the agent, not the LLM directly
            get_session_history=get_session_history,
            prompt=self.prompt_template,
            input_key="input"
        )

    def run(self, question):
        self._session_history.add_message("user", question)
        response = self.chain.invoke({"input": question, "history": self._session_history.format_history()}, config={"configurable": {"session_id": "default"}})
        answer = getattr(response, 'content', response) if not isinstance(response, str) else response
        self._session_history.add_message("ai", answer)
        return answer

def get_db_schema():
    engine = get_mysql_engine()
    inspector = inspect(engine)
    schema = ""
    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        columns = inspector.get_columns(table_name)
        for col in columns:
            schema += f"  - {col['name']} ({col['type']})\n"
    return schema
