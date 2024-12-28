import json
import os

class ChatHistoryManager:
    """
    A class to manage chat history for ensuring continuity in LLM interactions.
    """

    def __init__(self, history_file="chat_history.json", max_length=100):
        self.history_file = history_file
        self.max_length = max_length
        self.history = self.load_history()

    def load_history(self):
        """
        Load chat history from a file.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def save_history(self):
        """
        Save chat history to a file.
        """
        with open(self.history_file, "w") as file:
            json.dump(self.history, file, indent=2)

    def append_to_history(self, role, content):
        """
        Append a new message to the chat history.
        """
        self.history.append({"role": role, "content": content})

        # Ensure the history length does not exceed max_length
        if len(self.history) > self.max_length:
            self.history = self.history[-self.max_length:]

        self.save_history()

    def get_history(self):
        """
        Retrieve the chat history.
        """
        return self.history

    def clear_history(self):
        """
        Clear the chat history.
        """
        self.history = []
        self.save_history()

# Usage Example
if __name__ == "__main__":
    manager = ChatHistoryManager()

    # Append some interactions
    manager.append_to_history("user", "List all orders placed in the last month.")
    manager.append_to_history("assistant", "Sure, I can help with that. Do you want a summary or detailed data?")

    # Retrieve history
    print("Chat History:")
    print(manager.get_history())

    # Clear history
    manager.clear_history()
    print("History after clearing:", manager.get_history())
