# config.py
import os
from dotenv import load_dotenv
from typing import Dict

def load_config():
    # Load base .env file first
    load_dotenv(".env")

    # Get current environment from .env
    env = os.getenv("ENVIRONMENT", "dev")

    # Then load environment-specific file which can override base settings
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)

    config = {
        "ENVIRONMENT": env,
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CONCH_ENDPOINT": os.getenv("CONCH_ENDPOINT", "http://127.0.0.1:54001"),
        "VIRCHOW_ENDPOINT": os.getenv("VIRCHOW_ENDPOINT", "http://127.0.0.1:54002"),
        "MEDSAM_ENDPOINT": os.getenv("MEDSAM_ENDPOINT", "http://127.0.0.1:54003"),
        "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000"),
        "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    }

    # Validate required settings
    if not config["OPENAI_API_KEY"]:
        raise ValueError("OPENAI_API_KEY is not set")

    return config

config = load_config()
