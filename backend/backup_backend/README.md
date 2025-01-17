# Llama 3.2 1B Instruct Server Setup

Local FastAPI server using Llama 3.2 1B Instruct for response generation, accessible via REST API.

Install Required Packages:

- Method 1: `pip install -r requirements.txt`

- Method 2: `pip install fastapi uvicorn accelerate transformers`

You can get access from Meta to download Llama via Meta's HuggingFace repo

Install PyTorch:

1. If you are doing this on a CUDA-accelerated device, check your system's CUDA version: `nvidia-smi`

2. Visit https://pytorch.org/ and install the appropriate version. e.g. `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`

To run the Llama server:

1. Run in  one terminal: `uvicorn serve_llm:app --host 0.0.0.0 --port 8000` 
2. Run in another terminal: `test_llm_remote.py`
3. If you are running the `uvicorn` server on a different device, create an `.env` file in the root of your project folder and add the `SERVER_URL` variable e.g. `SERVER_URL=http://192.168.1.250:8000`
4. If you merely want to test Llama responses without setting up the server, run `test_llm_local.py`