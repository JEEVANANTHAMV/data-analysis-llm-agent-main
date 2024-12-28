import plotly.graph_objs as go
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from utils import convert_to_json, json_to_markdown_table

# Available tools schema
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "query_db",
            "description": "Fetch data from PostgreSQL database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "Complete and correct SQL query to fulfill user request.",
                    }
                },
                "required": ["sql_query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": "Plot Bar or Linechart to visualize the result of SQL query",
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "description": "Plot type (bar, line, or scatter)",
                    },
                    "x_values": {
                        "type": "array",
                        "description": "List of x values for plotting",
                        "items": {"type": "string"}
                    },
                    "y_values": {
                        "type": "array",
                        "description": "List of y-axis values for plotting",
                        "items": {"type": "number"}
                    },
                    "plot_title": {
                        "type": "string",
                        "description": "Descriptive title for the plot",
                    },
                    "x_label": {
                        "type": "string",
                        "description": "Label for the x-axis",
                    },
                    "y_label": {
                        "type": "string",
                        "description": "Label for the y-axis",
                    }
                },
                "required": ["plot_type", "x_values", "y_values", "plot_title", "x_label", "y_label"],
            },
        }
    }
]


async def run_postgres_query(sql_query, db_config, markdown=True):
    """
    Execute a PostgreSQL query using SQLAlchemy.

    Parameters:
    - sql_query (str): SQL query to execute.
    - db_config (dict): Dictionary containing database configuration.
    - markdown (bool): Whether to return results in Markdown format.

    Returns:
    - str or tuple: Markdown table if `markdown=True`, else (result, column_names).
    """
    # Construct the database URL
    db_url = f"postgresql://{db_config['db_user']}:{db_config['db_password']}@" \
             f"{db_config['db_host']}:{db_config['db_port']}/{db_config['db_name']}"
    
    # Create SQLAlchemy engine
    engine = create_engine(db_url)

    try:
        # Establish the connection
        with engine.connect() as connection:
            print("Connected to the database!")

            # Execute the query
            result_proxy = connection.execute(text(sql_query))

            # Fetch column names and rows
            column_names = result_proxy.keys()
            result = [dict(row) for row in result_proxy]

            if markdown:
                # Get result in JSON and Markdown
                json_data = {"columns": column_names, "data": result}
                markdown_data = json_to_markdown_table(json_data)
                return markdown_data

            return result, column_names
    except SQLAlchemyError as error:
        print("Error while executing the query:", error)
        if markdown:
            return f"Error while executing the query: {error}"
        return [], []
    finally:
        engine.dispose()
        print("SQLAlchemy connection disposed.")
async def plot_chart(x_values, y_values, plot_title, x_label, y_label, plot_type='line'):
    """
    Generate a bar chart, line chart, or scatter plot using Plotly.

    Parameters:
    - x_values (list): Input values for the x-axis.
    - y_values (list): Input values for the y-axis.
    - plot_title (str): Title of the plot.
    - x_label (str): Label for the x-axis.
    - y_label (str): Label for the y-axis.
    - plot_type (str): Type of plot to generate ('bar', 'line', or 'scatter').

    Returns:
    - plotly.graph_objs.Figure: The generated plot.
    """
    # Validate input lengths
    if not x_values or not y_values:
        raise ValueError("x_values and y_values cannot be empty.")

    if len(x_values) != len(y_values):
        raise ValueError("Lengths of x_values and y_values must be the same.")

    # Define plotly trace based on plot_type
    if plot_type == 'bar':
        trace = go.Bar(x=x_values, y=y_values)
    elif plot_type == 'scatter':
        trace = go.Scatter(x=x_values, y=y_values, mode='markers')
    elif plot_type == 'line':
        trace = go.Scatter(x=x_values, y=y_values, mode='lines+markers')
    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")

    # Create layout for the plot
    layout = go.Layout(
        title=plot_title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    # Create and return the figure
    fig = go.Figure(data=[trace], layout=layout)
    return fig
