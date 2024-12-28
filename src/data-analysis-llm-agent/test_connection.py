from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

def test_postgres_connection(db_config):
    """
    Test the connection to a PostgreSQL database using SQLAlchemy.

    Parameters:
    - db_config (dict): Dictionary containing database configuration.
      Example:
      {
          "db_name": "my_database",
          "db_user": "my_user",
          "db_password": "my_password",
          "db_host": "localhost",
          "db_port": "5432"
      }

    Returns:
    - str: Success or error message.
    """
    # Construct the database URL
    db_url = f"postgresql://{db_config['db_user']}:{db_config['db_password']}@" \
             f"{db_config['db_host']}:{db_config['db_port']}/{db_config['db_name']}"
    
    # Create SQLAlchemy engine
    engine = create_engine(db_url)

    try:
        # Attempt to connect to the database
        with engine.connect() as connection:
            print("Connected to the database successfully!")
            return "Connection successful!"
    except SQLAlchemyError as error:
        error_message = f"Connection failed: {error}"
        print(error_message)
        return error_message
    finally:
        engine.dispose()
        print("Connection closed.")
