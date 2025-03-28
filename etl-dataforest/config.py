import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Config as FlaskConfig


PROJECT_DIR = Path(__file__).parent.parent
ENV_PATH = PROJECT_DIR / ".env"


load_dotenv(ENV_PATH)


class Config(FlaskConfig):
    PROJECT_DIR = PROJECT_DIR

    # Application
    APP_PORT = os.getenv("APP_PORT", 80)
    APP_HOST = os.getenv("APP_HOST")
    APP_ENV = os.getenv("APP_ENV", "production")
    APP_SECRET = os.getenv("APP_SECRET")
    APP_DEBUG = os.getenv("APP_DEBUG", APP_ENV == "development")
    APP_MODULE = os.getenv("APP_MODULE", "dataforest")
    APP_DIR = PROJECT_DIR / APP_MODULE

    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = APP_ENV == "development"

    # Static
    STATIC_DIR = PROJECT_DIR / "static"

    # Flask
    DEBUG = APP_DEBUG
    TESTING = os.getenv("APP_TESTING", APP_ENV == "testing")
    SECRET_KEY = APP_SECRET

    @classmethod
    def validate_settings(cls):
        if ENV_PATH.exists():
            logging.info(f"Loaded .env file from {ENV_PATH}")
        else:
            logging.warning(
                f"No .env file found at {ENV_PATH}. Using system environment variables."
            )

        required_vars = [
            "APP_HOST",
            "APP_SECRET",
            "DB_HOST",
            "DB_PORT",
            "DB_USER",
            "DB_PASS",
            "DB_NAME",
        ]

        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")

        if cls.APP_PORT is None or not isinstance(cls.APP_PORT, (int, str)):
            raise ValueError("APP_PORT must be a valid integer.")

        if cls.DB_PORT is None or not isinstance(cls.DB_PORT, (int, str)):
            raise ValueError("DB_PORT must be a valid integer.")

        if cls.APP_ENV not in ["development", "testing", "production"]:
            raise ValueError(
                "APP_ENV must be one of 'development', 'testing', or 'production'."
            )
