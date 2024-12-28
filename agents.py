from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq
from history import ChatHistoryManager
from tools import query_database, summarize_schema, extract_requirements, plot_chart
from prompts import Prompts
from models import DatabaseSchema, QueryResult, VisualizationConfig

class DataAnalysisAgent:
    def __init__(self, db_config):
        self.db_config = db_config
        self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
        self.history_manager = ChatHistoryManager()
        self.prompts = Prompts()

        # Define tools
        self.tools = [
            Tool(name="Query Database", func=query_database, description="Execute SQL queries on the database."),
            Tool(name="Summarize Schema", func=summarize_schema, description="Summarize the schema of the database."),
            Tool(name="Extract Requirements", func=extract_requirements, description="Extract requirements from a user query."),
            Tool(name="Plot Chart", func=plot_chart, description="Generate visualizations for query results."),
        ]

        # Initialize the LangChain agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )

    def summarize_schema(self, prompt):
        """
        Step 1: Summarize the schema of the database.
        """
        response = self.llm.run(prompt)
        schema_summary = DatabaseSchema.from_response(response)  # Use DatabaseSchema for structured representation
        return schema_summary

    def execute_query(self, sql_query):
        """
        Step 4: Execute the SQL query and fetch results.
        """
        raw_results = query_database(sql_query, self.db_config)
        if isinstance(raw_results, str):  # Error case
            return {"error": raw_results}
        query_result = QueryResult.from_raw_results(raw_results)  # Use QueryResult for structured results
        return query_result

    def visualize_results(self, results, visualization_config):
        """
        Step 5: Generate visualizations for the query results.
        """
        try:
            config = VisualizationConfig(**visualization_config)  # Validate visualization config using the model
            chart = plot_chart(
                x_values=[row[config.x] for row in results],
                y_values=[row[config.y] for row in results],
                title=config.title,
                x_label=config.x,
                y_label=config.y,
                plot_type=config.type
            )
            return chart
        except Exception as e:
            return {"error": f"Failed to generate visualization: {e}"}

    def run(self, user_input):
        """
        Execute the full data analysis workflow.
        """
        chat_history = self.history_manager.get_history()

        # Summarize schema
        schema_summary_prompt = self.prompts.schema_summary_prompt()
        schema_summary = self.summarize_schema(schema_summary_prompt)

        # Extract requirements
        requirements = self.extract_requirements(user_input["query"], schema_summary)
        if "error" in requirements:
            return {"error": "Could not extract requirements from the query."}

        # Generate SQL
        sql_query = self.generate_sql(requirements)
        if not sql_query:
            return {"error": "Could not generate an SQL query from the requirements."}

        # Execute SQL
        results = self.execute_query(sql_query)
        if "error" in results:
            return results

        # Visualization
        if "visualization" in requirements:
            visualization_config = requirements["visualization"]
            chart = self.visualize_results(results["data"], visualization_config)
            return {"chart": chart}

        return {"data": results["data"]}
