

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from setup_llm import setup_llm
from functions import function_mapping, call_function

# Initialize the FastAPI app
app = FastAPI()

# Load the LLM pipeline when the server starts
print("Initializing the LLM pipeline...")
llm_pipeline = setup_llm()

if not llm_pipeline:
    raise RuntimeError("Failed to initialize the pipeline. Ensure model and tokenizer are correctly configured.")

# Define the input format for the API
class Query(BaseModel):
    conversation_history: list

# Prompt template to guide the LLM
PROMPT_TEMPLATE = """
You are a function selector chatbot. Based on the user's input, choose the best function from the following:
1. weather: Provides weather information for a location.
2. news: Summarizes news about a topic.
3. math: Solves a mathematical expression.

Output the function name and arguments as a single string in the format:
"function_name, arg1, arg2, ..."
Example: "weather, New York"
"""

@app.get("/health")
def health_check():
    return {'status': 'ok'}

@app.post("/gen_response")
async def gen_response(query: Query):
    """
    Accepts conversation history, determines which function to execute, and returns the result.
    """
    try:
        # Add the prompt to the conversation history
        conversation_history = [{"role": "system", "content": PROMPT_TEMPLATE}] + query.conversation_history

        # Generate a response using the LLM pipeline
        response = llm_pipeline(
            conversation_history,
            truncation=True,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=1.0,
            max_new_tokens=256,
        )

        # Extract the generated text from the LLM response
        llm_reply = response[0]['generated_text']

        # Parse the response to identify function and arguments
        try:
            function_name, *args = llm_reply.split(", ")
            function_name = function_name.strip()
            args = [arg.strip() for arg in args]

            # Execute the chosen function
            if function_name in function_mapping:
                result = call_function(function_name, args)
                return {"response": result}
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Function '{function_name}' is not recognized."
                )

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid response format from LLM. Expected 'function_name, arg1, arg2, ...'."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
