def validate_db_config(db_config):
    """
    Validates the database configuration dictionary.
    """
    required_keys = ["user", "password", "host", "port", "dbname"]
    for key in required_keys:
        if key not in db_config:
            raise ValueError(f"Missing required database configuration key: {key}")


def format_table_schema(schema):
    """
    Formats the table schema into a readable string for display.
    """
    return "\n".join([f"{col}: {dtype}" for col, dtype in schema.items()])
