# biotune.ai

## 1. setup environment variables

for `.env` files with `.example` at then, remove the `.example` from the filename
- e.g. `.env.docker.example` ---> `.env.docker`

## 2a. set up and run the service locally

uses variables stored in `.env` 

set up a dedicated virtual environment to run the service
```bash
# (install uv)
# curl -LsSf https://astral.sh/uv/install.sh | sh
# https://docs.astral.sh/uv/getting-started/installation/

uv python install 3.11

uv sync
```

start the service
```bash
# development
uv run fastapi dev --host 127.0.0.1 --port 8000 service.py

# production
uv run uvicorn service:app --host 127.0.0.1 --port 8000
# OR
uv run fastapi run --host 127.0.0.1 --port 8000 service.py
```

## 2b. run in a Docker container

uses variables stored in `.env.docker`

build the Docker image
```bash
docker build -t biotune-ai .
```

run the Docker container service
```bash
docker compose up
```

## 3. run the other services

clone frontend from https://github.com/IshanG97/biotune-ai-create

refer to the repo pages and setup accordingly


--- Built during AI x Cancer Hack - Jan 2025, Cambridge, United Kingdom ---


## Team

Ananya Bhalla - [GitHub](https://github.com/AnanyaBhalla), [LinkedIn](https://www.linkedin.com/in/ananyabhalla/)

Ellen Schrader - [GitHub](https://github.com/ellen-schrader), [LinkedIn](https://www.linkedin.com/in/ellen-schrader/)

Ishan Godawatta - [GitHub](https://github.com/IshanG97), [LinkedIn](https://www.linkedin.com/in/ishan-godawatta/)

William Stark - [GitHub](https://github.com/williamstarkbio), [LinkedIn](https://www.linkedin.com/in/williamstarkbio/)