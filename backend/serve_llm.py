from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.setup_llm import setup_llm

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

@app.get("/health")
def health_check():
    return {'status': 'ok'}

@app.post("/gen_response")
async def gen_response(query: Query):
    """
    Accepts conversation history and generates a response.
    """
    try:
        response = llm_pipeline(
            query.conversation_history,
            truncation=True,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=1.0,
            max_new_tokens=256,
        )
        reply = response[0]['generated_text']
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")