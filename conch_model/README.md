# CONCH model REST API classification service

Standalone FastAPI service that serves the CONCH model.


## set up and run the service

set up a dedicated virtual environment to run the service
```bash
pyenv install 3.11

pyenv virtualenv 3.11 conch_model

pyenv local conch_model

pip install -r requirements.txt
```

start the service
```bash
fastapi run --host 127.0.0.1 --port 54001 service.py
```

manually request classification for an image
```bash
# e.g.
IMAGE_PATH="/data/tcga-brca/fdcfe8e5-34c9-4675-933b-d588a3dd2cb9.uploaded/TCGA-BH-A0AZ-01Z-00-DX1.E20051E8-DEEF-48E5-B519-40777DDBC96B.svs"
curl -X GET "http://127.0.0.1:54001/process/${IMAGE_PATH}" -H "accept: application/json"
```

service documentation:
http://127.0.0.1:54001/docs

NOTE: The service is designed to run locally and currently doesn't incorporate authentication or other security features.
