import os

# Database Configuration
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "your_username"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "dbname": os.getenv("DB_NAME", "your_database"),
}

# API Keys and Model Configurations
api_config = {
    "groq_api_key": os.getenv("GROQ_API_KEY", "your_groq_api_key"),
    "model_name": os.getenv("MODEL_NAME", "mixtral-8x7b-32768"),
}

# Application Settings
app_settings = {
    "log_file": os.getenv("LOG_FILE", "chatbot.log"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "page_title": os.getenv("PAGE_TITLE", "Data Analysis LLM Agent"),
    "items_per_page": int(os.getenv("ITEMS_PER_PAGE", "10")),
}
