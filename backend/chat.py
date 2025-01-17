import re
from dotenv import load_dotenv
from conch_model.classify_cancer import get_cancer_subtype
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

function_mapping = {
    "get_cancer_subtype": get_cancer_subtype,  # Added this function
}

def parse_llm_response(response):
    """
    Parse the LLM response to identify function calls and arguments.
    """
    pattern = r"^(\w+)\s*,\s*(.+)$"
    match = re.match(pattern, response)
    if match:
        function_name = match.group(1)
        arguments = match.group(2)
        return function_name, arguments
    else:
        return None, None

def chat_with_openai():
    PROMPT_TEMPLATE = """
    You are a function selector chatbot. Based on the user's input, choose the best function from the following:
    1. get_cancer_subtype: Classifies the subtype of cancer based on an image path.

    Output the function name and arguments as a single string in the format:
    "function_name, arg1, arg2, ..."
    Example: "get_cancer_subtype, /path/to/image.jpg"

    If you don't have enough information to call a function, ask the user a clarifying question.
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

            # Parse the LLM response for function calls
            function_name, arguments = parse_llm_response(assistant_reply)
            if function_name and function_name in function_mapping:
                try:
                    # Call the mapped function
                    result = function_mapping[function_name](arguments)
                    print("Function Result:", result)

                    # Add function result to the conversation history
                    conversation_history.append({"role": "assistant", "content": result})
                except Exception as e:
                    print(f"Error executing function '{function_name}': {e}")
            else:
                # Add the assistant's conversational reply to the conversation history
                conversation_history.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"Error connecting to OpenAI API: {e}")
            break  # Stop the loop on persistent errors

if __name__ == "__main__":
    chat_with_openai()
