import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from agents import DataAnalysisAgent, extract_table_names

# Streamlit UI
st.title("Database Analysis with InnoSynth")
st.sidebar.header("Configuration")

# Collect database credentials from the user
db_user = st.sidebar.text_input("Database User", placeholder="Enter username")
db_password = st.sidebar.text_input("Database Password", placeholder="Enter password", type="password")
db_host = st.sidebar.text_input("Host", placeholder="Enter host (e.g., localhost or IP address)")
db_port = st.sidebar.number_input("Port", min_value=1, max_value=65535, value=5432, step=1)
db_name = st.sidebar.text_input("Database Name", placeholder="Enter database name")

# Check if all fields are filled
if not all([db_user, db_password, db_host, db_port, db_name]):
    st.sidebar.warning("Please fill in all database configuration fields.")
else:
    db_config = {
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
        "dbname": db_name
    }
    st.sidebar.write("Database credentials loaded successfully.")

    # Initialize the DataAnalysisAgent
    agent = DataAnalysisAgent(db_config)

    # Define system instructions with enhanced prompt engineering
    system_instructions = """
Remember:
- Before generating an answer, first inspect the database schema and preview sample data from each table.
- This ensures that the SQL query is accurate and tailored to the available columns and data.
- When generating SQL, always embed table names in escaped double quotes.
- For example, the SQL should be:
  SELECT \"BranchName\", COUNT(*) AS count 
  FROM \"globalanalytics\" 
  GROUP BY \"BranchName\" 
  HAVING COUNT(*) > 1;
"""

    # User input for query
    st.subheader("Enter Your Query")
    user_query = st.text_area("Query", placeholder="E.g., Find all employees with salaries above $100,000.")
    # Append the system instructions to the user query to guide the agent
    full_query = f"{user_query}\n\nSystem Instructions:\n{system_instructions}"

    if st.button("Analyze Database"):
        if user_query.strip():
            with st.spinner("Analyzing..."):
                try:
                    # Analyze the user query using the agent
                    result = agent.analyze_database(full_query)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        # Display the generated SQL query and matched table
                        st.success("SQL Query Generated:")
                        st.markdown(result['output'], unsafe_allow_html=True)
                except SQLAlchemyError as e:
                    st.error(f"Database connection failed: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a query.")

    # Display database structure in the sidebar
    if st.sidebar.checkbox("Show Database Structure"):
        st.sidebar.subheader("Database Tables")
        try:
            tables = extract_table_names(db_config)
            if isinstance(tables, dict) and "error" in tables:
                st.sidebar.error(tables["error"])
            else:
                for table in tables:
                    st.sidebar.write(f"- {table['table_name']}")
        except SQLAlchemyError as e:
            st.sidebar.error(f"Failed to fetch tables: {str(e)}")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {str(e)}")
