from dotenv import load_dotenv
import os

load_dotenv()

ENV: str = "DEVELOPMENT"
DB_HOST: str = os.getenv("DB_HOST")
DB_USER: str = os.getenv("DB_USER")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")
DB_NAME: str = os.getenv("DB_NAME")
EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
JWT_SECRET: str = os.getenv("JWT_SECRET")