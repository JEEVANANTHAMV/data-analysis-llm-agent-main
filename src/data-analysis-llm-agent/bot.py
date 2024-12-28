import requests
import logging
import json

# Groq API settings
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = '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'

# Main ChatBot class
class ChatBot:
    def __init__(self, system, tools, tool_functions, model="llama-3.3-70b-versatile"):
        self.system = system
        self.tools = tools
        self.tool_functions = tool_functions
        self.model = model
        self.messages = []
        self.exclude_functions = ["plot_chart"]
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def _send_request(self, payload):
        """Send a request to the Groq API."""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Groq API Error: {response.status_code} - {response.text}")
            raise Exception(f"Groq API Error: {response.status_code} - {response.text}")

    def __call__(self, message):
        """Handle user input and generate a response."""
        self.messages.append({"role": "user", "content": message})
        response_message = self.execute()

        if response_message.get("content"):
            self.messages.append({"role": "assistant", "content": response_message["content"]})

        logging.info(f"User message: {message}")
        logging.info(f"Assistant response: {response_message['content']}")

        return response_message

    def execute(self):
        """Send the message history to the Groq API and get the assistant's response."""
        payload = {
            "model": self.model,
            "messages": self.messages,
            "functions": self.tools,
        }
        response = self._send_request(payload)
        assistant_message = response["choices"][0]["message"]
        return assistant_message

    def call_function(self, tool_call):
        """Execute a function call requested by the assistant."""
        function_name = tool_call["function"]["name"]
        function_to_call = self.tool_functions[function_name]
        function_args = json.loads(tool_call["function"]["arguments"])
        logging.info(f"Calling {function_name} with {function_args}")
        function_response = function_to_call(**function_args)

        return {
            "tool_call_id": tool_call["id"],
            "role": "tool",
            "name": function_name,
            "content": function_response,
        }

    def call_functions(self, tool_calls):
        """Process tool calls iteratively."""
        function_responses = []
        for tool_call in tool_calls:
            function_responses.append(self.call_function(tool_call))

        # Add tool responses to the conversation
        for res in function_responses:
            self.messages.append({**res, "content": str(res["content"])})

        # Generate the next response after tool calls
        response_message = self.execute()
        return response_message, function_responses