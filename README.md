# biotune.ai

## 1. setup environement variables

refer to `examples/` - you will need to create `.env` (and `.env.docker` if you are using Docker) and place them in the root of the project folder. 

tip: copy-paste the existing example files, remove the .example at then end, and add the correct variables per your configuration

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

refer to the repo pages and setup accordingly


--- Built during AI x Cancer Hack - Jan 2025, Cambridge, United Kingdom ---


## Team

Ananya Bhalla - [GitHub](https://github.com/AnanyaBhalla), [LinkedIn](https://www.linkedin.com/in/ananyabhalla/)

Ellen Schrader - [GitHub](https://github.com/ellen-schrader), [LinkedIn](https://www.linkedin.com/in/ellen-schrader/)

Ishan Godawatta - [GitHub](https://github.com/IshanG97), [LinkedIn](https://www.linkedin.com/in/ishan-godawatta/)

William Stark - [GitHub](https://github.com/williamstarkbio), [LinkedIn](https://www.linkedin.com/in/williamstarkbio/)