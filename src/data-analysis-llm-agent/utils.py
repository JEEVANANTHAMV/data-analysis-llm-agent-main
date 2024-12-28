def generate_postgres_table_info_query(schema_table_pairs):
    """
    Generate a query to retrieve table and column metadata from a PostgreSQL database.
    
    Parameters:
    schema_table_pairs (list of tuples): A list of schema and table pairs (schema, table).
    
    Returns:
    str: The SQL query to retrieve table and column information.
    """
    query = """
    SELECT
        cols.table_schema,
        cols.table_name,
        cols.column_name,
        cols.data_type,
        coalesce(com.description, '') as column_description
    FROM
        information_schema.columns cols
    LEFT JOIN
        pg_class cl ON cl.relname = cols.table_name
    LEFT JOIN
        pg_description com ON com.objoid = cl.oid AND com.objsubid = cols.ordinal_position
    WHERE
        (cols.table_schema, cols.table_name) IN ({});
    """.format(', '.join(["('{}', '{}')".format(schema, table) for schema, table in schema_table_pairs]))
    return query


def format_table_info(results, columns):
    """
    Format table information for display.
    
    Parameters:
    results (list): Query results containing table and column metadata.
    columns (list): Column names for the results.
    
    Returns:
    str: Formatted table information string.
    """
    table_info = ""
    current_table = None

    for row in results:
        table_schema = row[columns.index('table_schema')]
        table_name = row[columns.index('table_name')]
        column_name = row[columns.index('column_name')]
        data_type = row[columns.index('data_type')]
        column_description = row[columns.index('column_description')]

        if current_table != table_name:
            if current_table is not None:
                table_info += "\n\n"
            table_info += f"""Table Name: "{table_schema}"."{table_name}"\n"""
            table_info += f"----------\n"
            current_table = table_name
            table_info += f"Following are Column Name(Datatype) and Description:\n"

        table_info += f"{column_name}({data_type})"
        if column_description:
            table_info += f" - {column_description}\n"
        else:
            table_info += '\n'

    return table_info


def format_sample_data(column_names, data_records):
    """
    Format sample data for display.
    
    Parameters:
    column_names (list): List of column names.
    data_records (list of tuples): List of data rows.
    
    Returns:
    str: Formatted sample data string.
    """
    formatted_data = ""
    for col_name in column_names:
        # Get unique non-empty values for the column
        values = set(record[column_names.index(col_name)] for record in data_records if record[column_names.index(col_name)] is not None and record[column_names.index(col_name)] != '')
        if values:  # Check if values exist
            formatted_data += f"{col_name}: "
            sample_values = ', '.join(str(value) for value in list(values)[:3])  # Display first 3 unique values
            if len(values) > 3:
                sample_values += ", ..."
            formatted_data += sample_values + '\n'

    return formatted_data


def generate_sample_data_query(schema, table, N):
    """
    Generate a query to retrieve sample data from a PostgreSQL table.
    
    Parameters:
    schema (str): Schema name.
    table (str): Table name.
    N (int): Number of sample rows to fetch.
    
    Returns:
    str: SQL query to fetch sample data.
    """
    return f"""SELECT * FROM "{schema}"."{table}" ORDER BY RANDOM() LIMIT {N};"""


# Data conversion utilities
def convert_to_json(rows, column_names):
    """
    Convert query results to JSON format.
    
    Parameters:
    rows (list of tuples): Query results as rows.
    column_names (list): Column names corresponding to the rows.
    
    Returns:
    dict: JSON representation of the query results.
    """
    results = []
    for row in rows:
        row_dict = dict(zip(column_names, row))
        results.append(row_dict)
    return {"columns": column_names, "data": results}


def json_to_markdown_table(json_data):
    """
    Convert JSON data to a Markdown table format.
    
    Parameters:
    json_data (dict): JSON data with "columns" and "data" keys.
    
    Returns:
    str: Markdown-formatted table as a string.
    """
    # Extract columns and data from JSON
    columns = json_data["columns"]
    data = json_data["data"]

    # Generate Markdown table header
    markdown_table = "| " + " | ".join(columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    # Generate Markdown table rows
    for row in data:
        markdown_table += "| " + " | ".join(str(row[column]) for column in columns) + " |\n"

    return markdown_table
