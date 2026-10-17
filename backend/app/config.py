from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://finsight:finsight@localhost:5432/finsight"
    secret_key: str = "dev-secret-key"
    allowed_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()
