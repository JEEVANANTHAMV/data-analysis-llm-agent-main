from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq
from tools import query_database, extract_table_names, extract_table_schema, generate_graph
from utils import validate_db_config

class DataAnalysisAgent:
    def __init__(self, db_config):
        """
        Initializes the Data Analysis Agent.
        """
        validate_db_config(db_config)
        self.db_config = db_config
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0,
            api_key="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"
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
            name="Extract Table Schema",
            func=lambda table_name: extract_table_schema(table_name, db_config),
            description="Extracts the schema of a specified table."
        ),
        Tool(
            name="Generate Graph",
            func=lambda input_data: generate_graph(
                data=input_data['data'],
                graph_type=input_data.get('graph_type', 'line'),  # Provide default values
                title=input_data.get('title', 'Graph Title'),
                labels=input_data.get('labels', None),
                xlabel=input_data.get('xlabel', 'X Axis'),
                ylabel=input_data.get('ylabel', 'Y Axis')
            ),
            description="Generates various types of graphs based on input data."
        )
        
    ]

def initialize_data_analysis_agent(db_config, llm):
    """
    Initializes the LangChain agent with the necessary tools.
    """
    tools = create_tools(db_config, llm)
    return initialize_agent(tools, llm, agent="structured-chat-zero-shot-react-description", verbose=True, handle_parsing_errors=True)
