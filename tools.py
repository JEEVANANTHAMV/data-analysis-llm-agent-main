from sqlalchemy import create_engine, text
import plotly.graph_objs as go

# Tool: Query Database
def query_database(sql_query, db_config):
    """
    Executes a SQL query on the database and returns the results.

    Args:
        sql_query (str): The SQL query to execute.
        db_config (dict): Database configuration containing host, port, user, password, and dbname.

    Returns:
        list[dict]: A list of dictionaries representing the query results.
    """
    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@" \
             f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result_proxy = conn.execute(text(sql_query))
            results = [dict(row) for row in result_proxy]
            return results
    except Exception as e:
        return {"error": str(e)}
    finally:
        engine.dispose()

# Tool: Summarize Schema
def summarize_schema(db_config):
    """
    Summarizes the schema of the database by retrieving table and column information.

    Args:
        db_config (dict): Database configuration.

    Returns:
        dict: A dictionary summarizing the schema, where keys are table names and values are column info.
    """
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public';
    """
    schema_info = query_database(query, db_config)
    schema_summary = {}
    for row in schema_info:
        table_name = row["table_name"]
        column_details = f"{row['column_name']} ({row['data_type']})"
        if table_name not in schema_summary:
            schema_summary[table_name] = []
        schema_summary[table_name].append(column_details)
    return schema_summary


# Tool: Plot Chart
def plot_chart(x_values, y_values, title, x_label, y_label, plot_type="bar"):
    """
    Generates a chart using Plotly.

    Args:
        x_values (list): Values for the x-axis.
        y_values (list): Values for the y-axis.
        title (str): Title of the chart.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        plot_type (str): Type of chart ("bar", "line", "scatter").

    Returns:
        str: HTML representation of the chart.
    """
    if plot_type == "bar":
        trace = go.Bar(x=x_values, y=y_values)
    elif plot_type == "line":
        trace = go.Scatter(x=x_values, y=y_values, mode="lines+markers")
    elif plot_type == "scatter":
        trace = go.Scatter(x=x_values, y=y_values, mode="markers")
    else:
        raise ValueError("Invalid plot type")

    layout = go.Layout(title=title, xaxis=dict(title=x_label), yaxis=dict(title=y_label))
    fig = go.Figure(data=[trace], layout=layout)
    return fig.to_html()

# Tools Registration
tools = [
    {
        "name": "Query Database",
        "func": query_database,
        "description": "Execute SQL queries on the database."
    },
    {
        "name": "Summarize Schema",
        "func": summarize_schema,
        "description": "Summarize the database schema."
    },
    {
        "name": "Extract Requirements",
        "func": extract_requirements,
        "description": "Extract requirements from a user's natural language query."
    },
    {
        "name": "Plot Chart",
        "func": plot_chart,
        "description": "Generate visualizations for query results."
    }
]
