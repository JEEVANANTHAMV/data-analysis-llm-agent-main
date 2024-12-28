import streamlit as st
import logging
from agents import DataAnalysisAgent
from config import db_config
from prompts import Prompts
from history import ChatHistoryManager

# Configure logging
logging.basicConfig(
    filename="chatbot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

# Initialize Streamlit app
st.set_page_config(page_title="Data Analysis LLM Agent", layout="wide")
st.title("Data Analysis LLM Agent")

# Sidebar for PostgreSQL configuration
st.sidebar.title("PostgreSQL Configuration")
db_host = st.sidebar.text_input("Host", value=db_config["host"])
db_port = st.sidebar.text_input("Port", value=db_config["port"])
db_user = st.sidebar.text_input("Username", value=db_config["user"])
db_password = st.sidebar.text_input("Password", type="password", value=db_config["password"])
db_name = st.sidebar.text_input("Database Name", value=db_config["dbname"])

# Update database configuration
db_config.update({
    "host": db_host,
    "port": db_port,
    "user": db_user,
    "password": db_password,
    "dbname": db_name,
})

# Initialize components
history_manager = ChatHistoryManager()
prompts = Prompts()
agent = DataAnalysisAgent(db_config)

# Test connection
st.sidebar.title("Database Connection")
if st.sidebar.button("Test Connection"):
    try:
        schema_summary = agent.summarize_schema(prompts.schema_summary_prompt())
        st.sidebar.success("Connection successful!")
        st.sidebar.write("Schema Summary:")
        st.sidebar.write(schema_summary)
    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")

# Main user interaction
st.subheader("Enter your query")
user_query = st.text_area("Query", height=150)
if st.button("Submit Query"):
    if not user_query.strip():
        st.error("Please enter a query.")
    else:
        try:
            # Retrieve chat history for context
            chat_history = history_manager.get_history()
            user_query_with_history = {
                "history": chat_history,
                "query": user_query,
            }

            # Run the agent workflow
            response = agent.run(user_query_with_history)

            # Append to chat history
            history_manager.append_to_history("user", user_query)
            history_manager.append_to_history("assistant", str(response))

            # Display response
            if isinstance(response, dict) and "chart" in response:
                st.plotly_chart(response["chart"], use_container_width=True)
            elif isinstance(response, str):
                st.markdown(response)
            else:
                st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display chat history
st.sidebar.subheader("Chat History")
chat_history = history_manager.get_history()
if chat_history:
    for message in chat_history:
        role = message["role"].capitalize()
        content = message["content"]
        st.sidebar.markdown(f"**{role}:** {content}")

# Option to clear chat history
if st.sidebar.button("Clear History"):
    history_manager.clear_history()
    st.sidebar.success("Chat history cleared.")