from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    price_provider: str = "csv"
    weather_provider: str = "sample"
    disease_provider: str = "demo"
    ocr_provider: str = "none"
    mandi_csv: str = "data/mandi.csv"
    class Config:
        env_file = ".env"

settings = Settings()
EOF