# biotune.ai 

--- ⭐️ Awarded 2nd place at the UK's first AI x Cancer Biology Hackathon, University of Cambridge ⭐️ ---

Foundation models have the potential to shape the next frontier in cancer research. Just in the past year, over 160 biological foundation models have been released but their incorporation into the academic toolbox remains slow. The onus of evaluating and benchmarking models to select the right one for each research question lies upon individual labs and teams. 

Over a period of 24 hours, we built biotune.ai - an AI assistant and chat interface designed to simplify interaction with foundation models and streamline access to AI tools for biologists.





## Team

Ananya Bhalla - [GitHub](https://github.com/AnanyaBhalla), [LinkedIn](https://www.linkedin.com/in/ananyabhalla/)

Ellen Schrader - [GitHub](https://github.com/ellen-schrader), [LinkedIn](https://www.linkedin.com/in/ellen-schrader/)

Ishan Godawatta - [GitHub](https://github.com/IshanG97), [LinkedIn](https://www.linkedin.com/in/ishan-godawatta/)

William Stark - [GitHub](https://github.com/williamstarkbio), [LinkedIn](https://www.linkedin.com/in/williamstarkbio/)


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

activate the environment to run commands without the `uv run` prefix
```bash
source .venv/bin/activate
```

install `pre-commit` git hook scripts
```bash
pre-commit install
```

start the service
```bash
# development
fastapi dev --host 127.0.0.1 --port 8000 service.py

# production
uvicorn service:app --host 127.0.0.1 --port 8000
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

