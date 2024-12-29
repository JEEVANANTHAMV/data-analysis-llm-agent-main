from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import numpy as np

def query_database(sql_query, db_config):
    """
    Executes a SQL query and returns results or errors.
    """
    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@" \
             f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result_proxy = conn.execute(text(sql_query))
            # Fetch all rows into memory while the connection is active
            results = result_proxy.fetchall()
            # Convert results to a list of dictionaries
            column_names = result_proxy.keys()
            return [dict(zip(column_names, row)) for row in results]
    except Exception as e:
        return {"error": str(e)}
    finally:
        engine.dispose()


def extract_table_names(db_config):
    """
    Retrieves table names from the database.
    """
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    return query_database(query, db_config)


def extract_table_schema(table_name, db_config):
    """
    Retrieves the schema (columns and data types) for a specific table.
    """
    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table_name.strip()}';
    """
    return query_database(query, db_config)

def generate_graph(data, graph_type="line", title="Graph Title", labels=None, **kwargs):
    plt.figure(figsize=(10, 5))  # Set the figure size

    if graph_type == "line":
        for i, key in enumerate(data):
            plt.plot(data[key], label=labels[i] if labels else key, **kwargs)
    elif graph_type == "bar":
        indices = np.arange(len(data[list(data.keys())[0]]))  # Assuming all data sets are of the same length
        width = 0.8 / len(data)
        for i, key in enumerate(data):
            plt.bar(indices + i * width, data[key], width=width, label=labels[i] if labels else key, **kwargs)
    elif graph_type == "scatter":
        for i, key in enumerate(data):
            plt.scatter(data[key][0], data[key][1], label=labels[i] if labels else key, **kwargs)
    elif graph_type == "histogram":
        for i, key in enumerate(data):
            plt.hist(data[key], bins=kwargs.get('bins', 10), label=labels[i] if labels else key, **kwargs)

    plt.title(title)
    plt.legend()
    plt.xlabel(kwargs.get('xlabel', 'X Axis'))
    plt.ylabel(kwargs.get('ylabel', 'Y Axis'))
    plt.show()
