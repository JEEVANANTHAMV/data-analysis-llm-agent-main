from sqlalchemy import create_engine, text
import plotly.graph_objs as go

# Database Connection and Query Execution
def query_database(sql_query, db_config):
    """
    Executes a SQL query on the database and returns results.

    Parameters:
    - sql_query (str): The SQL query to execute.
    - db_config (dict): Database configuration containing host, port, user, password, and dbname.

    Returns:
    - list: A list of dictionaries containing the query results.
    - str: Error message if the query fails.
    """
    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@" \
             f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            return [dict(row) for row in result]
    except Exception as e:
        return f"Error executing query: {e}"

# Schema Summarization
def summarize_schema(db_config):
    """
    Summarizes the schema of the database by fetching table and column details.

    Parameters:
    - db_config (dict): Database configuration.

    Returns:
    - dict: A dictionary summarizing the schema.
    - str: Error message if the query fails.
    """
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public';
    """
    schema = query_database(query, db_config)
    if isinstance(schema, str):  # Error case
        return schema

    schema_summary = {}
    for row in schema:
        table = row["table_name"]
        column = row["column_name"]
        dtype = row["data_type"]
        if table not in schema_summary:
            schema_summary[table] = []
        schema_summary[table].append(f"{column} ({dtype})")
    return schema_summary

# Chart Generation
def plot_chart(x_values, y_values, title, x_label, y_label, plot_type="bar"):
    """
    Generates a chart using Plotly.

    Parameters:
    - x_values (list): Values for the x-axis.
    - y_values (list): Values for the y-axis.
    - title (str): Chart title.
    - x_label (str): Label for the x-axis.
    - y_label (str): Label for the y-axis.
    - plot_type (str): Type of plot ('bar', 'line', 'scatter').

    Returns:
    - str: HTML representation of the chart.
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
    return go.Figure(data=[trace], layout=layout).to_html()

# JSON-to-Markdown Table Conversion
def json_to_markdown_table(json_data):
    """
    Converts JSON data to a Markdown table format.

    Parameters:
    - json_data (list): List of dictionaries representing the data.

    Returns:
    - str: Markdown-formatted table as a string.
    """
    if not json_data:
        return "No data available."

    headers = json_data[0].keys()
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in json_data:
        table += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"

    return table
