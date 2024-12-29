from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq
from tools import query_database, extract_table_names, extract_table_schema
from prompts import Prompts  # Import prompts for reusable logic
from utils import validate_db_config

class DataAnalysisAgent:
    def __init__(self, db_config):
        """
        Initializes the Data Analysis Agent.
        """
        # Validate database configuration
        validate_db_config(db_config)

        self.db_config = db_config

        # Initialize LangChain-Groq LLM
        self.llm = ChatGroq(
            model_name="mixtral-8x7b-32768",
            temperature=0,
            api_key="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"
        )

        # Initialize LangChain agent with tools
        self.agent = initialize_data_analysis_agent(db_config, self.llm)

    def analyze_database(self, user_query):
        """
        Analyzes the database based on user input and returns the result.

        Steps:
        1. Identify the most relevant table(s).
        2. Extract the schema of the table.
        3. Generate SQL based on the user's query and schema.
        4. Execute the SQL query and return results.
        """
        try:
            result = self.agent.run(user_query)
            return result
        except Exception as e:
            return {"error": f"An error occurred during analysis: {e}"}


def create_tools(db_config, llm):
    """
    Creates a list of tools for the LangChain agent.
    """
    return [
        Tool(
            name="Query Database",
            func=lambda query: query_database(query, db_config),
            description="Executes SQL queries on the database."
        ),
        Tool(
            name="Extract Table Names",
            func=lambda _: extract_table_names(db_config),  # Accepts input but ignores it
            description="Extracts table names from the database."
        ),
        Tool(
            name="Extract Table Schema",
            func=lambda table_name: extract_table_schema(table_name, db_config),
            description="Extracts the schema of a specified table."
        ),
        Tool(
            name="Generate SQL Query",
            func=lambda input_data: generate_sql_query(input_data["user_query"], input_data["table_schema"], llm),
            description="Generates an SQL query from user input and table schema."
        ),
    ]

def generate_sql_query(user_query, table_schema, llm):
    """
    Generates an SQL query using LangChain-Groq and the prompt from prompts.py.
    """
    # Use the prompt from Prompts
    prompt = Prompts.sql_generation_prompt({
        "user_query": user_query,
        "table_schema": table_schema
    })
    response = llm.invoke([("system", "You are a helpful SQL assistant."), ("human", prompt)])
    return response.content


def initialize_data_analysis_agent(db_config, llm):
    """
    Initializes the LangChain agent with the necessary tools.
    """
    tools = create_tools(db_config, llm)
    return initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
