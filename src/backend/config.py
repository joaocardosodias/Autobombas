import os
import warnings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def _get_jwt_secret():
    secret = os.getenv("JWT_SECRET")
    return secret


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("SUPABASE_URL", ""))
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    JWT_SECRET: str = _get_jwt_secret()
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8


settings = Settings()
