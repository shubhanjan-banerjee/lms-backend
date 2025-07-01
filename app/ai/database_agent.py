from app.ai.agent import get_ai_agent

# Create the SQL agent
agent_executor = get_ai_agent()

print("\n--- LangChain SQL Agent Ready ---")

def run_agent_query():
    try:
        queries = [
            "List all developers and their assigned project roles.",
            "What skills does Jane Smith have and at what proficiency level?",
            "Which employees have 'JavaScript' skill at 'Proficient' level or higher? Show their names and proficiency.",
            "How many employees are 'Frontend Developer'?"
        ]
        for i, q in enumerate(queries, 1):
            if not q.strip():
                print(f"Query {i} is empty, skipping.")
                continue
            print(f"\nQuery {i}: {q}")
            try:
                response = agent_executor.invoke(q)
                # If response is an object with 'content', extract it
                if hasattr(response, 'content'):
                    response = response.content
                print(f"Agent Response: {response}")
            except Exception as agent_exc:
                print(f"Agent error for Query {i}: {agent_exc}")
    except Exception as e:
        print(f"\nAn error occurred during agent execution: {e}")
        print("Check the 'verbose' output above for detailed trace if available.")

if __name__ == "__main__":
    run_agent_query()