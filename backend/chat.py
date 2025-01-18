from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import re
from dotenv import load_dotenv
import os
from openai import OpenAI
import shutil
from pathlib import Path
from datetime import datetime
import base64

# Initialize the FastAPI app
app = FastAPI()

# Create and mount uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Request models
class ImageUrl(BaseModel):
    url: str

class ContentItem(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None

class Message(BaseModel):
    role: str
    content: Union[str, List[ContentItem]]

class ChatRequest(BaseModel):
    messages: List[Message]

class FunctionRequest(BaseModel):
    function_name: str
    arguments: List[str]

# System prompt template
PROMPT_TEMPLATE = """
You are an AI assistant specialized in analyzing medical images and cancer subtypes.
After analyzing any images, you should determine if you need to call any functions. If you don't need to call a function, provide your analysis normally.

Available functions:
1. get_cancer_subtype: Classifies the subtype of cancer based on an image path.

If you determine a function should be called, respond with an output in the format:
"function_name, arg1, arg2, ..."
Example: "get_cancer_subtype, /uploads/filename.jpg"

"""

def parse_llm_response(response: str) -> tuple[Optional[str], Optional[str]]:
    """Parse the LLM response to identify function calls and arguments."""
    # Clean the response
    response = response.strip()
    # Remove userStyle tags
    response = re.sub(r'<userStyle>.*?</userStyle>', '', response)
    # Remove any quotes
    response = response.replace('"', '')
    response = response.strip()
    
    print(f"Cleaned response: {response}")  # Debug log
    
    pattern = r"^(\w+)\s*,\s*(.+)$"
    match = re.match(pattern, response)
    if match:
        function_name = match.group(1)
        arguments = match.group(2).strip()
        print(f"Matched - function: {function_name}, args: {arguments}")  # Debug log
        return function_name, arguments
    return None, None

def get_cancer_subtype(image_path: str) -> str:
    """Classify cancer subtype from an image."""
    try:
        # Remove any leading slashes and get the full path
        image_path = image_path.lstrip('/')
        full_path = os.path.join(os.getcwd(), image_path)
        
        if not os.path.exists(full_path):
            return f"Error: Image not found at {image_path}"
            
        # Here you would typically:
        # 1. Load the image
        # 2. Run your classification model
        # 3. Return the results
        
        # For now, return a detailed placeholder response
        return f"""
Cancer subtype analysis for image at {image_path}:
- Tissue Type: Histopathological specimen
- Primary Classification: Carcinoma
- Suggested Subtype: Ductal carcinoma
- Confidence: 85%
- Additional Notes: Sample shows characteristic cellular organization...
"""
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

# Function mapping
function_map = {
    "get_cancer_subtype": get_cancer_subtype,
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "gpt-4o"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads"""
    try:
        #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #unique_filename = f"{timestamp}_{file.filename}"
        unique_filename = f"{file.filename}"
        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return the full URL path that will be accessible
        file_url = f"{TEMP_PATH}/{unique_filename}"
        return {
            "url": file_url,
            "mimeType": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint that processes messages and handles image analysis"""
    try:
        conversation_history = [{"role": "system", "content": PROMPT_TEMPLATE}]
        
        for msg in request.messages:
            if isinstance(msg.content, str):
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:  # List[ContentItem]
                content_parts = []
                for item in msg.content:
                    if item.type == "text":
                        content_parts.append({
                            "type": "text",
                            "text": item.text
                        })
                    elif item.type == "image_url" and item.image_url:
                        # Extract just the relative path from the full URL
                        url_path = item.image_url["url"]
                        # Remove any domain/host part if present
                        if "://" in url_path:
                            url_path = url_path.split("/uploads/")[-1]
                            url_path = f"uploads/{url_path}"
                        else:
                            url_path = url_path.lstrip('/')
                        
                        image_path = os.path.join(os.getcwd(), url_path)
                        print(f"Attempting to read image from: {image_path}")  # Debug log
                        
                        # Read and encode the image
                        try:
                            with open(image_path, "rb") as image_file:
                                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                                content_parts.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{encoded_image}"
                                    }
                                })
                                # Store original path for function calls
                                original_path = item.image_url["url"]
                        except Exception as e:
                            print(f"Error reading image: {str(e)}")
                            raise HTTPException(
                                status_code=400,
                                detail=f"Error reading image file: {str(e)}"
                            )

                conversation_history.append({
                    "role": msg.role,
                    "content": content_parts
                })

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            max_tokens=500
        )

        assistant_reply = response.choices[0].message.content
        print(f"Assistant reply: {assistant_reply}")  # Debug log

        # Parse for function calls after image analysis
        
        function_name, arguments = parse_llm_response(assistant_reply)

        # In your chat endpoint, update the function call section:
        if function_name and function_name in function_map:
            try:
                # Pass the argument directly without splitting
                result = function_map[function_name](arguments)
                
                # Return both the original response and the function result
                return {
                    "response": f"""I've analyzed the image and called the classification function.
        Original response: {assistant_reply}
        Function result: {result}""",
                    "function_call": {
                        "name": function_name,
                        "result": result
                    }
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing function '{function_name}': {str(e)}"
                )

        return {"response": assistant_reply}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/function")
async def function_endpoint(request: FunctionRequest):
    """Direct function execution endpoint"""
    try:
        if request.function_name not in function_map:
            raise HTTPException(
                status_code=400,
                detail=f"Function '{request.function_name}' not found"
            )

        result = function_map[request.function_name](*request.arguments)
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing function: {str(e)}")

if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    parse_llm_response("get_cancer_subtype, uploads/tcga1.png")
    
    