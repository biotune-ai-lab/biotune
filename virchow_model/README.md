# Virchow model REST API service

Standalone FastAPI service that serves the Virchow model.


## set up and run the service

set up a dedicated virtual environment to run the service
```bash
pyenv install 3.11

pyenv virtualenv 3.11 virchow_model

pyenv local virchow_model

pip install -r requirements.txt
```

start the service
```bash
fastapi run --host 127.0.0.1 --port 54002 service.py
```


manually request classification for an image
```bash
# e.g.
IMAGE_FILENAME="breast.svs"
curl -X GET "http://127.0.0.1:54002/process/${IMAGE_FILENAME}" -H "accept: application/json"
```

service documentation:
http://127.0.0.1:54002/docs

NOTE: The service is designed to run locally and currently doesn't incorporate authentication or other security features.
