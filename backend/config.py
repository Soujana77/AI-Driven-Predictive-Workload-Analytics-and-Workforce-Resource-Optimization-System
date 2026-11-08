
import os
from pathlib import Path

from dotenv import load_dotenv

# Always load the environment file from the backend directory.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is missing. "
                "Please configure it in backend/.env"
            )
