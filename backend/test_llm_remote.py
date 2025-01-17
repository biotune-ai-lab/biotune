import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch the LLM server URL
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
GEN_RESPONSE_ENDPOINT = os.getenv("GET_RESPONSE_ENDPOINT", "/gen_response")
HEALTH_ENDPOINT = os.getenv("HEALTH_ENDPOINT", "/health")
gen_response = SERVER_URL+GEN_RESPONSE_ENDPOINT

# Step 1: Test if the LLM server is reachable
def _health_check_server(health_url):
    try:
        response = requests.get(health_url)
        if response.status_code == 200:
            print(f"LLM server health check passed at {health_url}.")
            return True
        else:
            print(f"Health check failed with status code {response.status_code}.")
            return False
    except Exception as e:
        print(f"Error testing LLM server URL: {e}")
        return False

def setup():
    if not _health_check_server(SERVER_URL+HEALTH_ENDPOINT):
        print("LLM server is not reachable. Exiting...")
        exit()

def chat_with_llm(initial_prompt):
    # Prompt engineer the LLM
    conversation_history = [
        {"role": "system", "content": initial_prompt}
    ]

    # Main interaction loop
    while True:
        input_text = input("Enter your text (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            print("Exiting...")
            break

        # Append the user's input to the conversation history
        conversation_history.append({"role": "user", "content": input_text})

        # Send request to the LLM server
        try:
            response = requests.post(gen_response, json={"conversation_history": conversation_history})
            if response.status_code == 200:
                reply = response.json().get("response", "No response generated")
                print("Generated Reply:", reply)

                # Add the assistant's reply to the conversation history
                conversation_history.append({"role": "assistant", "content": reply})
            else:
                print(f"Error from server: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error connecting to LLM server: {e}")

if __name__ == "__main__":
    setup()
    initial_prompt = "You are a pirate chatbot. Respond in 50 words or less. Make controversial statements."
    chat_with_llm(initial_prompt)