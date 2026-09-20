from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_url: str = "sqlite:///./sampatti_setu.db"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "sampatti_setu_photos"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    frontend_origin: str = "http://localhost:5500"

    # ---- Email (OTP delivery) ----
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    otp_expire_minutes: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
