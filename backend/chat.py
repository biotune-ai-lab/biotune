from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Fetch the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

def chat_with_openai():
    PROMPT_TEMPLATE = """
    You are a function selector chatbot. Based on the user's input, choose the best function from the following, but you should explain to the user:
    1. weather: Provides weather information for a location.
    2. news: Summarizes news about a topic.
    3. math: Solve only mathematical expressions.

    Output the function name and arguments as a single string in the format:
    "function_name, arg1, arg2, ..."
    Example: "weather, New York"
    """
    
    """
    Main interaction loop with OpenAI API.
    """
    # Instructions for the OpenAI model
    system_message = {
        "role": "system",
        "content": PROMPT_TEMPLATE
    }

    # Start conversation history
    conversation_history = [system_message]

    while True:
        user_input = input("Enter your text (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        # Add the user's message to the conversation history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Call OpenAI's API
            response = client.chat.completions.create(
                model="gpt-4o",  # Fixed model name typo
                messages=conversation_history,
                #temperature=0.7,  # Added back temperature
                #max_tokens=256   # Added back max_tokens
            )

            # Extract the assistant's reply - Updated for new response structure
            assistant_reply = response.choices[0].message.content
            print("\nAI Reply:", assistant_reply, "\n")

            # Add the assistant's reply to the conversation history
            conversation_history.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"Error connecting to OpenAI API: {e}")
            break  # Added break to prevent infinite loop on persistent errors

if __name__ == "__main__":
    chat_with_openai()