import os

from dotenv import load_dotenv


def load_config():
    if os.path.exists(
        ".env"
    ):  # this makes it so .env files override whatever other env vars have been loaded in
        load_dotenv(".env", override=True)

    config = {
        "OBJECT_STORAGE_API": os.getenv("OBJECT_STORAGE_API", "http://127.0.0.1:9090"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CONCH_ENDPOINT": os.getenv("CONCH_ENDPOINT", "http://127.0.0.1:54001"),
        "VIRCHOW_ENDPOINT": os.getenv("VIRCHOW_ENDPOINT", "http://127.0.0.1:54002"),
        "MEDSAM_ENDPOINT": os.getenv("MEDSAM_ENDPOINT", "http://127.0.0.1:54003"),
    }

    # Validate required settings
    if not config["OPENAI_API_KEY"]:
        raise ValueError("OPENAI_API_KEY is not set")

    return config


config = load_config()
