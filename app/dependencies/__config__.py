from os import getenv
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from typing import Any

# Define the application directory based on the location of the current file
APP_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Directories
    APP_DIR: Path = APP_DIR

    # Encryption Variables
    ALGORITHM: SecretStr = SecretStr(getenv("ALGORITHM"))
    SECRET_KEY: SecretStr = SecretStr(getenv("SECRET_KEY"))

    # Database URL
    DATABASE_URL: SecretStr = SecretStr(getenv("DATABASE_URL"))

    # Redis Database
    REDIS_HOST: SecretStr = SecretStr(getenv("REDIS_HOST"))
    REDIS_PORT: SecretStr = SecretStr(getenv("REDIS_PORT"))
    REDIS_DB: SecretStr = SecretStr(getenv("REDIS_DB"))
    REDIS_PASSWORD: SecretStr = SecretStr(getenv("REDIS_PASSWORD"))
    REDIS_MAX_CONNECTIONS: int = 20

    # Admin Information
    ADMIN_USERNAME: SecretStr = SecretStr(getenv("ADMIN_USERNAME"))
    ADMIN_EMAIL: SecretStr = SecretStr(getenv("ADMIN_EMAIL"))
    ADMIN_FIRST_NAME: SecretStr = SecretStr(getenv("ADMIN_FIRST_NAME"))
    ADMIN_LAST_NAME: SecretStr = SecretStr(getenv("ADMIN_LAST_NAME"))
    ADMIN_PASSWORD: SecretStr = SecretStr(getenv("ADMIN_PASSWORD"))

    # Redis Cache Expiration time 4 Hours
    CACHE_EXPIRATION: int = 14400

    # JWT Token Expiration time in hours
    JWT_EXPIRE: int = 1

    # FastAPI core settings
    FASTAPI_PROPERTIES: dict = {
        "title": "FastAPI Application",
        "description": "A robust and efficient API designed for modern applications.",
        "summary": "Developed and Maintained by Amir Debram",
        "version": "1.0.0",
        "terms_of_service": "https://www.domain.org/terms/",
        "contact": {
            "name": "API Support - Amir Debram",
            "url": "https://www.domain.org/support/",
            "email": "amirdebram@gmail.com"
        },
        "license_info": {
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
        }
    }

    # Toggle for enabling/disabling documentation endpoints
    DISABLE_DOCS: bool = False

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """Returns FastAPI initialization kwargs."""
        fastapi_kwargs = self.FASTAPI_PROPERTIES.copy()
        if self.DISABLE_DOCS:
            fastapi_kwargs.update({
                "openapi_url": None,
                "docs_url": None,
                "redoc_url": None
            })
        return fastapi_kwargs

    # Encryption Variables
    @property
    def algorithm(self) -> str:
        """Safely retrieves the algorithm."""
        return self.ALGORITHM.get_secret_value()

    @property
    def secret_key(self) -> str:
        """Safely retrieves the secret key."""
        return self.SECRET_KEY.get_secret_value()

    # Database URL
    @property
    def database_url(self) -> str:
        """Safely retrieves the database URL and ensures it's a string."""
        url = self.DATABASE_URL.get_secret_value()
        if not url:
            raise ValueError("Database URL not configured")
        return url

    # Redis Database
    @property
    def redis_host(self) -> str:
        """Safely retrieves the Redis host."""
        return self.REDIS_HOST.get_secret_value()
    
    @property
    def redis_port(self) -> int:
        """Safely retrieves the Redis port."""
        return self.REDIS_PORT.get_secret_value()
    
    @property
    def redis_db(self) -> int:
        """Safely retrieves the Redis database."""
        return self.REDIS_DB.get_secret_value()
    
    @property
    def redis_password(self) -> str:
        """Safely retrieves the Redis password."""
        return self.REDIS_PASSWORD.get_secret_value()

    # Admin Information
    @property
    def admin_username(self) -> str:
        """Safely retrieves the Redis password."""
        return self.ADMIN_USERNAME.get_secret_value()

    @property
    def admin_email(self) -> str:
        """Safely retrieves the Redis password."""
        return self.ADMIN_EMAIL.get_secret_value()

    @property
    def admin_firstname(self) -> str:
        """Safely retrieves the Redis password."""
        return self.ADMIN_FIRST_NAME.get_secret_value()

    @property
    def admin_lastname(self) -> str:
        """Safely retrieves the Redis password."""
        return self.ADMIN_LAST_NAME.get_secret_value()

    @property
    def admin_password(self) -> str:
        """Safely retrieves the Redis password."""
        return self.ADMIN_PASSWORD.get_secret_value()

# Create an instance of settings to be imported by other modules
settings = Settings()
