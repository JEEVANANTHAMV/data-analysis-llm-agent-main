import streamlit as st
from dotenv import load_dotenv
import logging
from plotly.graph_objs import Figure
from test_connection import test_postgres_connection

from tools import tools_schema, run_postgres_query, plot_chart
from bot import ChatBot

# Load environment variables from .env file
load_dotenv("../.env")

# Configure logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

MAX_ITER = 5

# Initialize Streamlit app
st.set_page_config(page_title="Data Analysis LLM Agent", layout="wide")
st.title("Data Analysis LLM Agent")

# Sidebar for PostgreSQL configuration
st.sidebar.title("PostgreSQL Configuration")
db_host = st.sidebar.text_input("Host")
db_port = st.sidebar.text_input("Port", value="5432")
db_user = st.sidebar.text_input("Username")
db_password = st.sidebar.text_input("Password", type="password")
db_name = st.sidebar.text_input("Database Name")

if st.sidebar.button("Test Connection"):
    db_config = {
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password,
        "db_host": db_host,
        "db_port": db_port
    }
    result = test_postgres_connection(db_config)
    if "successful" in result.lower():
        st.sidebar.success(result)
    else:
        st.sidebar.error(result)

# Function to initialize chatbot
def initialize_chatbot():
    system_message = """You are an expert in data analysis. You will provide valuable insights for business users based on their requests.
    Before responding, ensure the user's query pertains to data analysis on the provided schema, else decline.
    If a user requests data, you will build an SQL query based on the user's request for the PostgreSQL database and call the `query_db` tool to fetch data from the database with the correct/relevant query that gives the correct result.
    
    Follow these guidelines:
    - If you need certain inputs to proceed or are not sure about anything, ask questions, but try to use your intelligence to understand user intention.
    - Provide a business-friendly response without technical jargon.
    - Provide rich Markdown responses, using tables for data and clear formatting.
    - Limit top N queries to 5 and inform the user of the limit.
    - Limit results to 10 when users request all records and inform them.
    - Ensure SQL queries cast date and numeric columns into readable formats.
    """
    
    tool_functions = {
        "query_db": lambda query: run_postgres_query(query, {
            "db_host": db_host,
            "db_port": db_port,
            "db_user": db_user,
            "db_password": db_password,
            "db_name": db_name
        }),
        "plot_chart": plot_chart
    }
    return ChatBot(system_message, tools_schema, tool_functions)

# Initialize or load the chatbot
if "bot" not in st.session_state:
    st.session_state["bot"] = initialize_chatbot()

bot = st.session_state["bot"]

# User input section
user_input = st.text_input("Enter your query:")

if st.button("Submit"):
    if user_input:
        # Display the user's query
        st.markdown(f"**User:** {user_input}")

        # Get the bot's response
        response_message = bot(user_input)

        # Display the bot's response
        st.markdown(f"**Assistant:** {response_message.content}")

        # Handle tool calls and iterations
        cur_iter = 0
        tool_calls = response_message.tool_calls
        while cur_iter < MAX_ITER:
            if tool_calls:
                # Call the necessary tools and get responses
                bot.messages.append(response_message)
                response_message, function_responses = bot.call_functions(tool_calls)

                # Display bot's updated response
                st.markdown(f"**Assistant:** {response_message.content}")

                # Display charts if any
                for function_res in function_responses:
                    if isinstance(function_res["content"], Figure):
                        st.plotly_chart(function_res["content"])
                tool_calls = response_message.tool_calls
            else:
                break
            cur_iter += 1