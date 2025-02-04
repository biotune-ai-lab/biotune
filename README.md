# biotune.ai


## 1a. set up and run the service locally

create `.env` file from template; update environment variable values if needed
```bash
cp .env.example .env
```

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
```


## 1b. run service in a Docker container

create `.env.docker` file from template; update environment variable values if needed
```bash
cp .env.docker.example .env.docker
```

build the Docker image
```bash
docker build -t biotune-ai .
```

run the Docker container service
```bash
docker compose up
```


## 2. run the other services

clone frontend from https://github.com/IshanG97/biotune-ai-create

refer to the repo pages and setup accordingly


--- Built during AI x Cancer Hack - Jan 2025, Cambridge, United Kingdom ---


## Team

Ananya Bhalla - [GitHub](https://github.com/AnanyaBhalla), [LinkedIn](https://www.linkedin.com/in/ananyabhalla/)

Ellen Schrader - [GitHub](https://github.com/ellen-schrader), [LinkedIn](https://www.linkedin.com/in/ellen-schrader/)

Ishan Godawatta - [GitHub](https://github.com/IshanG97), [LinkedIn](https://www.linkedin.com/in/ishan-godawatta/)

William Stark - [GitHub](https://github.com/williamstarkbio), [LinkedIn](https://www.linkedin.com/in/williamstarkbio/)
