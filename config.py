import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        if os.path.exists(".env"):  # Load .env file if it exists
            load_dotenv(".env", override=True)

        self.OBJECT_STORAGE_API = os.getenv(
            "OBJECT_STORAGE_API", "http://127.0.0.1:59090"
        )
        # self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
        self.MODEL = "deepseek-ai/DeepSeek-R1"
        self.CONCH_ENDPOINT = os.getenv("CONCH_ENDPOINT", "http://127.0.0.1:54001")
        self.VIRCHOW_ENDPOINT = os.getenv("VIRCHOW_ENDPOINT", "http://127.0.0.1:54002")
        self.MEDSAM_ENDPOINT = os.getenv("MEDSAM_ENDPOINT", "http://127.0.0.1:54003")

        # Validate required settings
        """ if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        """
        if not self.NEBIUS_API_KEY:
            raise ValueError("NEBIUS_API_KEY is not set")


# we could create a global config instance, tbd if we want to do this
# config = Config()
