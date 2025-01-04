from langchain.agents import Tool, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import query_database, extract_table_names, extract_database_schema_with_sample
from utils import validate_db_config

class DataAnalysisAgent:
    def __init__(self, db_config):
        """
        Initializes the Data Analysis Agent.
        """
        validate_db_config(db_config)
        self.db_config = db_config
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0,
            google_api_key="AIzaSyDKZz8Ckn_o-Pe4LRZBzmJcfGEVaZEWnJ8"  # Replace with your valid API key
        )
        self.agent = initialize_data_analysis_agent(db_config, self.llm)

    def analyze_database(self, user_query):
        """
        Analyzes the database based on user input and returns the result.
        """
        try:
            result = self.agent.invoke(user_query)
            return result
        except Exception as e:
            return {"error": f"An error occurred during analysis: {str(e)}"}

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
            func=lambda _: extract_table_names(db_config),
            description="Extracts table names from the database."
        ),
        Tool(
            name="Extract Database Schema with Sample",
            func=lambda table_name: extract_database_schema_with_sample(db_config),
            description=(
                "Extracts the schema of a database table and returns the first two rows "
                "as a sample along with the table schema."
            )
        )
    ]

def initialize_data_analysis_agent(db_config, llm):
    """
    Initializes the LangChain agent with the necessary tools.
    """
    tools = create_tools(db_config, llm)
    return initialize_agent(
        tools, 
        llm, 
        agent="structured-chat-zero-shot-react-description", 
        verbose=True, 
        handle_parsing_errors=True
    )
