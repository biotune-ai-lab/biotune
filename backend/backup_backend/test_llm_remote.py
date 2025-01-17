import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch the LLM server URL and endpoints
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
GEN_RESPONSE_ENDPOINT = os.getenv("GET_RESPONSE_ENDPOINT", "/gen_response")
HEALTH_ENDPOINT = os.getenv("HEALTH_ENDPOINT", "/health")
GEN_RESPONSE_URL = f"{SERVER_URL}{GEN_RESPONSE_ENDPOINT}"
HEALTH_URL = f"{SERVER_URL}{HEALTH_ENDPOINT}"

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
    if not _health_check_server(HEALTH_URL):
        print("LLM server is not reachable. Exiting...")
        exit()

def chat_with_llm():
    # Main interaction loop
    while True:
        input_text = input("Enter your text (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            print("Exiting...")
            break

        # Send request to the LLM server
        try:
            response = requests.post(GEN_RESPONSE_URL, json={"conversation_history": [{"role": "user", "content": input_text}]})
            if response.status_code == 200:
                llm_reply = response.json().get("response", "No response generated")

                # Ensure llm_reply is a string
                if isinstance(llm_reply, str):
                    print("LLM Reply:", llm_reply)
                else:
                    print("Unexpected response format from LLM. Please check the server output.")
            else:
                print(f"Error from server: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error connecting to LLM server: {e}")

if __name__ == "__main__":
    setup()
    chat_with_llm()
