import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Settings class to hold configuration values.

    Attributes:
        SERVER (str): Database server.
        USERNAME (str): Database username.
        PASSWORD (str): Database password.
        DATABASE_NAME (str): Database name.
        DATABASE_URL (str): Database URL.
        SECRET_KEY (str): Secret key for JWT.
        TEMP_DIR (str): Temporary directory for file uploads.
        CELERY_BROKER_URL (str): URL for Celery broker.
        CELERY_RESULT_BACKEND (str): URL for Celery result backend.
    """
    SERVER: str = 'your Database server'
    USERNAME: str = 'your Database username'
    PASSWORD: str = 'your Database password'
    DATABASE_NAME: str = 'your Database name'
    DATABASE_URL: str = f"mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE_NAME}"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    TEMP_DIR: str = os.getenv("TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp"))
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

settings = Settings()