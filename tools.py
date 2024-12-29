from sqlalchemy import create_engine, text


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
    WHERE table_name = '{table_name}';
    """
    return query_database(query, db_config)


def generate_sql_query(user_query, table_schema, llm):
    """
    Generates an SQL query based on user input and the given table schema using LangChain-Groq.
    """
    prompt = f"""
    User Query: {user_query}
    Table Schema: {table_schema}
    Generate an SQL query that satisfies the user's requirement.
    """
    response = llm.invoke([("system", "You are a helpful SQL assistant."), ("human", prompt)])
    return response.content
