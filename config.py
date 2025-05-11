from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    LLM_MODEL: str
    LLM_MAX_TOKENS: int
    LLM_TEMPERATURE: float
    INTENTS_FILE: str
    MODEL_DIR: str
    POSTGRES_URI: str

settings = Settings()
