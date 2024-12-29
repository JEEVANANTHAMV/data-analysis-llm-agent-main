import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from agents import DataAnalysisAgent, extract_table_names

# Initialize database configuration
db_config = {
    "user": "jeeva",
    "password": "E30q5#mTfsKl19",
    "host": "35.198.119.144",
    "port": 5432,
    "dbname": "jeeva_db"
}

agent = DataAnalysisAgent(db_config)

# Streamlit UI
st.title("Database Analysis with LangChain-Groq")
st.sidebar.header("Configuration")
st.sidebar.write("Database credentials loaded successfully.")

# User input for query
st.subheader("Enter Your Query")
user_query = st.text_area("Query", placeholder="E.g., Find all employees with salaries above $100,000.")

if st.button("Analyze Database"):
    if user_query.strip():
        with st.spinner("Analyzing..."):
            try:
                # Analyze the user query using the agent
                result = agent.analyze_database(user_query)
                print(result,"jeeva")
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Display the generated SQL query and matched table
                    st.success("SQL Query Generated:")
                    st.write(result)
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