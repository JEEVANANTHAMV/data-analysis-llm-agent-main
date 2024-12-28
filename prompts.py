class Prompts:
    """
    Centralized repository for system prompts used in the workflow.
    """

    @staticmethod
    def schema_summarization_prompt():
        return """
        You are an assistant summarizing a database schema.
        Task:
        - Extract table names, column names, and their data types.
        - Ensure the summary is concise and structured for analysis.
        Input: Database configuration or schema.
        Output: A structured summary in dictionary format.
        Example:
        {
            "table1": ["column1 (type1)", "column2 (type2)"],
            "table2": ["column1 (type1)"]
        }
        """

    @staticmethod
    def requirement_extraction_prompt(user_query, schema_summary):
        return f"""
        You are an assistant extracting requirements for SQL queries.
        Task:
        - Analyze the user's query and identify the intent (e.g., retrieve data, filter).
        - Identify relevant tables and columns based on the provided schema summary.
        - Extract filters, conditions, or visualization needs, if any.
        Input:
        - User Query: "{user_query}"
        - Schema Summary: {schema_summary}
        Output:
        {
            "intent": "retrieve",
            "tables": ["table1"],
            "columns": ["column1", "column2"],
            "filters": {"column1": "value"},
            "visualization": {
                "type": "bar",
                "x": "column1",
                "y": "column2",
                "title": "Chart Title"
            }
        }
        """

    @staticmethod
    def sql_generation_prompt(requirements):
        return f"""
        You are an assistant generating SQL queries from requirements.
        Task:
        - Generate a valid SQL query for a PostgreSQL database.
        - Include filters and conditions specified in the requirements.
        - Limit results to 10 rows for large datasets.
        Input: Requirements: {requirements}
        Output: A valid SQL query.
        Example: SELECT column1, column2 FROM table1 WHERE column1 = 'value' LIMIT 10;
        """

    @staticmethod
    def visualization_prompt(results, visualization):
        return f"""
        You are an assistant creating visualizations based on data.
        Task:
        - Generate a chart based on the provided data.
        - Use the specified plot type (e.g., bar, line, scatter).
        Input:
        - Results: {results}
        - Visualization Details: {visualization}
        Output: A visual representation of the data.
        """

    @staticmethod
    def result_interpretation_prompt(results):
        return f"""
        You are an assistant interpreting SQL query results.
        Task:
        - Provide a concise explanation of the data returned by the query.
        - Highlight key insights or trends visible in the data.
        Input: Query Results: {results}
        Output: A concise explanation of the results.
        """
