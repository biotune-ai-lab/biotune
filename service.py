import base64
import mimetypes
import os
import re
from typing import Dict, List, Optional, Union

import httpx
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

import models
from config import Config

# Initialize the FastAPI app
app = FastAPI()
config = Config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.LLM_MODEL == "gpt-4o":
    llm_client = OpenAI(api_key=config.LLM_API_KEY)
else:
    llm_client = OpenAI(
        base_url="https://api.studio.nebius.ai/v1/", api_key=config.LLM_API_KEY
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": f"{config.LLM_MODEL}"}


# Object storage services
@app.get("/bucket/{bucket_name}")
async def list_files(bucket_name: str):
    # Assuming you have defined OBJECT_STORAGE_API in your config/environment
    storage_api_url = f"{config.OBJECT_STORAGE_API}/bucket/{bucket_name}"

    async with httpx.AsyncClient() as client:
        response = await client.get(storage_api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()


@app.post("/bucket/{bucket_name}/upload")
async def upload_file(bucket_name: str, file: UploadFile = File(...)):
    try:
        # Debug log what we received
        print(f"Received file - name: {file.filename}, type: {file.content_type}")

        storage_api_url = f"{config.OBJECT_STORAGE_API}/bucket/{bucket_name}/upload"
        print(f"Forwarding to storage API: {storage_api_url}")

        # Read the file content
        file_content = await file.read()
        print(f"Read {len(file_content)} bytes from uploaded file")

        # Prepare the file for the storage API
        files = {"file": (file.filename, file_content, file.content_type)}

        print(f"Filename: {file.filename}")

        # Send to storage API
        async with httpx.AsyncClient() as client:
            print("Sending to storage API...")
            response = await client.post(storage_api_url, files=files)
            print(f"Storage API response status: {response.status_code}")

            # Make sure the storage API request was successful
            response.raise_for_status()

            # Return consistent response format
            return {
                "message": "File uploaded successfully",
                "url": f"/bucket/{bucket_name}/download/{file.filename}",  # Backend reference URL
                "mimeType": file.content_type,
            }

    except httpx.HTTPError as exc:
        error_msg = f"Storage API error: {str(exc)}"
        print(f"Error: {error_msg}")
        status_code = exc.response.status_code if hasattr(exc, "response") else 500
        raise HTTPException(status_code=status_code, detail=error_msg)

    except Exception as e:
        error_msg = f"Unexpected error during upload: {str(e)}"
        print(f"Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/bucket/{bucket_name}/download/{filename}")
async def download_file(bucket_name: str, filename: str):
    storage_api_url = (
        f"{config.OBJECT_STORAGE_API}/bucket/{bucket_name}/download/{filename}"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(storage_api_url)
            response.raise_for_status()

            # Handle content type here
            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )

            return Response(
                content=response.content,
                media_type=content_type,
                headers={"Content-Disposition": f"inline; filename={filename}"},
            )

    except httpx.HTTPError as exc:
        if hasattr(exc, "response") and exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        status_code = exc.response.status_code if hasattr(exc, "response") else 500
        raise HTTPException(
            status_code=status_code, detail=f"Storage service error: {str(exc)}"
        )


@app.delete("/bucket/{bucket_name}/delete/{filename}")
async def delete_file(bucket_name: str, filename: str):
    storage_api_url = (
        f"{config.OBJECT_STORAGE_API}/bucket/{bucket_name}/delete/{filename}"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(storage_api_url)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as exc:
        if hasattr(exc, "response") and exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        status_code = exc.response.status_code if hasattr(exc, "response") else 500
        raise HTTPException(
            status_code=status_code, detail=f"Storage service error: {str(exc)}"
        )


@app.post("/bucket/create/{bucket_name}")
async def create_bucket(bucket_name: str):
    storage_api_url = f"{config.OBJECT_STORAGE_API}/bucket/create/{bucket_name}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(storage_api_url)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as exc:
        if hasattr(exc, "response") and exc.response.status_code == 409:
            raise HTTPException(
                status_code=409, detail=f"Bucket {bucket_name} already exists"
            )

        status_code = exc.response.status_code if hasattr(exc, "response") else 500
        raise HTTPException(
            status_code=status_code, detail=f"Storage service error: {str(exc)}"
        )


# Request models
class ContentItem(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None


class Message(BaseModel):
    role: str
    content: Union[str, List[ContentItem]]


class ChatRequest(BaseModel):
    messages: List[Message]


def parse_llm_response(response: str) -> tuple[Optional[str], Optional[str]]:
    """Parse the LLM response to identify function calls and arguments."""
    # Clean the response
    response = response.strip()
    # Remove userStyle tags
    response = re.sub(r"<userStyle>.*?</userStyle>", "", response)
    # Remove any quotes
    response = response.replace('"', "")
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


async def get_image_analysis(image_path: str, endpoint) -> str:
    try:
        # Extract just the filename from the path
        filename = os.path.basename(image_path)

        endpoint_url = f"{endpoint}/process/{filename}"

        print(f"Making request to: {endpoint_url}")  # Debug print

        async with httpx.AsyncClient(timeout=30.0) as client:  # Add timeout
            response = await client.get(
                endpoint_url,
                headers={"accept": "application/json"},
            )

        print(f"Got response with status: {response.status_code}")  # Debug print

        if response.status_code != 200:
            error_text = await response.text()  # Get error details
            print(f"Error response: {error_text}")  # Debug print
            return f"Error: Failed to get prediction for {filename}"

        print(
            f"Response data: {response.text}"
        )  # Add this to see what you're getting back
        return response.text

    except httpx.TimeoutException:
        return "Error: Request timed out while waiting for the service"
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # Debug log
        return f"Error analyzing image: {str(e)}"


async def process_and_save_image(image_path: str, endpoint) -> str:
    try:
        # Extract just the filename from the path
        filename = os.path.basename(image_path)

        endpoint_url = f"{endpoint}/process/{filename}"

        print(f"Making request to: {endpoint_url}")  # Debug print
        # Make request to your model endpoint
        async with httpx.AsyncClient(timeout=30.0) as client:  # Add timeout
            response = await client.post(
                endpoint_url,
                headers={"accept": "application/json"},
            )

        print(f"Got response with status: {response.status_code}")  # Debug print

        if response.status_code != 200:
            error_text = await response.text()  # Get error details
            print(f"Error response: {error_text}")  # Debug print
            return f"Error: Failed to get prediction for {filename}"

        print(
            f"Response data: {response.text}"
        )  # Add this to see what you're getting back
        return response.text

    except httpx.TimeoutException:
        return "Error: Request timed out while waiting for the service"
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # Debug log
        return f"Error analyzing image: {str(e)}"


async def subtype_image(image_path: str) -> str:
    """Classify cancer subtype from an image."""
    result = await get_image_analysis(image_path, config.CONCH_ENDPOINT)
    return result


async def get_best_image(image_path: str) -> str:
    """Get image that most closely matches uploaded images."""
    result = await get_image_analysis(image_path, config.VIRCHOW_ENDPOINT)
    return result


async def segment_image_with_medsam(image_path: str) -> str:
    print("Error: Function not implemented yet, will do this with SAM")
    result = await process_and_save_image(image_path, config.SAM_ENDPOINT)
    return result


async def segment_image_with_sam(image_path: str) -> str:
    """Get image that most closely matches uploaded images."""
    result = await process_and_save_image(image_path, config.SAM_ENDPOINT)
    return result


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint that processes messages and handles image analysis"""
    try:
        conversation_history = [
            {"role": "system", "content": models.get_prompt(config.LLM_MODEL, "system")}
        ]

        for msg in request.messages:
            if isinstance(msg.content, str):
                conversation_history.append({"role": msg.role, "content": msg.content})
            else:  # List[ContentItem]
                content_parts = []
                for item in msg.content:
                    if item.type == "text":
                        content_parts.append({"type": "text", "text": item.text})
                    elif item.type == "image_url" and item.image_url:
                        url_path = item.image_url["url"]

                        # Extract filename from URL
                        filename = url_path.split("/")[-1]

                        try:
                            response = await download_file("uploads", filename)
                            if isinstance(response, dict) and "error" in response:
                                raise HTTPException(
                                    status_code=400, detail=response["error"]
                                )
                            image_data = response.body
                            encoded_image = base64.b64encode(image_data).decode("utf-8")
                            content_parts.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{encoded_image}"
                                    },
                                }
                            )
                        except Exception as e:
                            print(f"Error reading image from object storage: {str(e)}")
                            raise HTTPException(
                                status_code=400,
                                detail=f"Error reading image file: {str(e)}",
                            )

                conversation_history.append(
                    {"role": msg.role, "content": content_parts}
                )

        response = llm_client.chat.completions.create(
            model=config.LLM_MODEL, messages=conversation_history, max_tokens=500
        )

        assistant_reply = response.choices[0].message.content
        print(f"Assistant reply: {assistant_reply}")  # Debug log

        # Parse for function calls after image analysis
        function_name, arguments = parse_llm_response(assistant_reply)

        if function_name and function_name in function_map:
            try:
                # Get the model's prediction
                result = await function_map[function_name](arguments)

                # Load the domain model that maps to the function name
                domain_model = models.get_domain_model(function_name)

                # Get domain model's system prompt
                domain_model_system_prompt = models.get_prompt(domain_model, "system")

                # Get domain model's analysis prompt and wrap the result in
                analysis_prompt = models.get_prompt(
                    domain_model, function_name, result=result
                )

                # Get GPT's interpretation of the domain model's system and analysis prompt
                interpretation_response = llm_client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": domain_model_system_prompt},
                        {"role": "user", "content": analysis_prompt},
                    ],
                    max_tokens=500,
                )

                interpreted_result = interpretation_response.choices[0].message.content

                return {
                    "response": interpreted_result,
                    "function_call": {
                        "name": function_name,
                        "raw_result": result,
                        "interpreted_result": interpreted_result,
                    },
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing function '{function_name}': {str(e)}",
                )

        return {"response": assistant_reply}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


# Function mapping
function_map = {
    "subtype_image": subtype_image,
    "get_best_image": get_best_image,
    "segment_image_with_medsam": segment_image_with_medsam,
    "segment_image_with_sam": segment_image_with_sam,
}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
