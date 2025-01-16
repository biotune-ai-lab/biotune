from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
from datetime import datetime
import os

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def log_ip_address(request: Request):
    ip = request.client.host
    timestamp = datetime.now().isoformat()
    
    # Create or load existing log file
    log_file = 'ip_logs.json'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # Add new entry
    logs.append({
        "ip": ip,
        "timestamp": timestamp,
        "endpoint": str(request.url),
        "method": request.method
    })
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, data: PredictionInput):
    # Log IP before processing request
    log_ip_address(request)
    return {"prediction": result}