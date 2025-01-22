from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import re
import os
from openai import OpenAI
import shutil
from pathlib import Path
from datetime import datetime
import base64
import requests
from minio_api import MinioApi
from config import config

# Initialize the FastAPI app
app = FastAPI()
minio_api = MinioApi()
client = OpenAI(api_key=config["OPENAI_API_KEY"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MinIO services
@app.get("/bucket/{bucket_name}")
async def list_files(bucket_name: str):
    return await minio_api.list_files(bucket_name)

@app.post("/bucket/{bucket_name}/upload")
async def upload_file(bucket_name: str, file: UploadFile):
    return await minio_api.upload_file(bucket_name, file)

@app.get("/bucket/{bucket_name}/download/{filename}")
async def download_file(bucket_name: str, filename: str):
    return await minio_api.download_file(bucket_name, filename)

@app.delete("/bucket/{bucket_name}/delete/{filename}")
async def delete_file(bucket_name: str, filename: str):
    return await minio_api.delete_file(bucket_name, filename)

@app.post("/bucket/create/{bucket_name}")
async def create_bucket(bucket_name: str):
    return await minio_api.create_bucket(bucket_name)

@app.delete("/bucket/delete/{bucket_name}")
async def delete_bucket(bucket_name: str):
    return await minio_api.delete_bucket(bucket_name)

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
After analyzing any images, you should determine if you need to call any functions. If you don't need to call a function, provide your analysis normally. Provide responses in plain text without markdown.

Available functions:
1. get_cancer_subtype: Classifies the subtype of cancer based on an image path. This function uses Conch, a Vision-Language Model trained on pathology data.
2. get_best_image: Find the image most similar to the uploaded image based on morphology. This function uses Virchow, a foundation model for pathology.
3. get_segmentation_run: Segments the image. Uses MedSAM.

If the user asks you for further assistance or evaluation or task, determine if a function should be called, with an output in the format:
"function_name, argument"
Examples: 
"get_cancer_subtype, tcga_10.png"

We only have three filenames, tcga_10.png, tcga_11.png, tcga_20.png
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
        # Extract just the filename from the path
        filename = os.path.basename(image_path)
        # Make request to your model endpoint
        response = requests.get(f"{config['CONCH_ENDPOINT']}/process/{filename}", 
                              headers={"accept": "application/json"})
        
        if response.status_code != 200:
            return f"Error: Failed to get prediction for {filename}"
            
        return response.text
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def get_best_image(image_path: str) -> str:
    """Get image that most closely matches uploaded images."""
    try:
        # Extract just the filename from the path
        filename = os.path.basename(image_path)
        # Make request to your model endpoint
        response = requests.get(f"{config['VIRCHOW_ENDPOINT']}/process/{filename}", 
                              headers={"accept": "application/json"})
        
        if response.status_code != 200:
            return f"Error: Failed to get prediction for {filename}"
            
        return response.text
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def get_segmentation_run(image_path: str) -> str:
    """Get image that most closely matches uploaded images."""
    try:
        # Extract just the filename from the path
        filename = os.path.basename(image_path)
        #DOWNLOAD_PATH=f"{config["MINIO_ENDPOINT"]}/images/medsam_segmented/{Path(filename).stem}_segmented.png"
        
        # Make request to your model endpoint
        response = requests.get(f"{config['MEDSAM_ENDPOINT']}/process/{filename}", 
                              headers={"accept": "application/json"})
        
        if response.status_code != 200:
            return f"Error: Failed to get prediction for {filename}"
            
        return response.text
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"
    

# Function mapping
function_map = {
    "get_cancer_subtype": get_cancer_subtype,
    "get_best_image": get_best_image,
    "get_segmentation_run": get_segmentation_run,
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "gpt-4o"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads to MinIO storage"""
    try:
        bucket_name = "uploads"  # Default bucket for uploads
        
        # Ensure bucket exists
        await minio_api.create_bucket(bucket_name)
        
        # Upload file to MinIO
        result = await minio_api.upload_file(bucket_name, file)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Return the file information
        return {
            "url": f"/{bucket_name}/download/{file.filename}",  # URL for downloading the file
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
                        url_path = item.image_url["url"]
                        
                        # Extract filename from URL
                        filename = url_path.split('/')[-1]
                        
                        bucket_name = "uploads"

                        try:
                            # Get the file from MinIO instead of local filesystem
                            image_data = minio_api.download_file(bucket_name, filename)
                            
                            # Read the data and encode it
                            encoded_image = base64.b64encode(image_data.read()).decode('utf-8')
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            })
                        except Exception as e:
                            print(f"Error reading image from MinIO: {str(e)}")
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

        if function_name and function_name in function_map:
            try:
                # Get the model's prediction
                result = function_map[function_name](arguments)

                FUNCTION_PROMPT = "You are a medical AI assistant specializing in cancer diagnosis interpretation. Provide responses in plain text without markdown."
                
                if "cancer" in function_name: 
                   # Create a prompt for GPT to interpret the results
                    analysis_prompt = f"""
    Based on the image analysis, the model has detected the following:

    {result}

    Please provide a clear, professional summary of these findings, explaining what they mean 
    for a medical professional. Include:
    1. The primary cancer type identified
    2. The confidence levels for each prediction
    3. Any relevant clinical implications

    Please format your response in a clear, organized way.
    """
                elif "best" in function_name:
                    # Create a prompt for GPT to interpret the results
                    analysis_prompt = f"""
    Based on the image analysis, the model has detected the following:

    {result}

    Please provide a clear, professional summary of these findings, explaining what they mean 
    for a medical professional. Include:
    1. The primary cancer type identified
    2. The confidence levels for each prediction
    3. Any relevant clinical implications

    Please format your response in a clear, organized way.
    """
                else: #segmentation
                    # Create a prompt for GPT to interpret the results
                    analysis_prompt = f"""Tell the user the image has been segmented and can be found in the downloads folder. If the user is unhappy with the segmentation performance, tell them to click on Explore AI models.
    """
                # Get GPT's interpretation
                interpretation_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": FUNCTION_PROMPT},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=500
                )

                interpreted_result = interpretation_response.choices[0].message.content

                return {
                    "response": interpreted_result,
                    "function_call": {
                        "name": function_name,
                        "raw_result": result,
                        "interpreted_result": interpreted_result
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    #parse_llm_response("get_cancer_subtype, uploads/tcga1.png")
    
    