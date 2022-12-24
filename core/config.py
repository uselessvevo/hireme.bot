""" Bot and database settings """
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / os.getenv("ENV_FILE", ".env"))

DEBUG = bool(os.getenv("DEBUG"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_BASE_URL = "www.example.domain"

# Database settings
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_NAME")

POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Redis settings
REDIS_PROT = os.getenv("REDIS_PROT", "redis")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = os.getenv("REDIS_DB")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Scrapper server settings
SCRAPPER_HOST = os.getenv("SCRAPPER_HOST", "127.0.0.1")
SCRAPPER_PORT = os.getenv("SCRAPPER_PORT", "8080")
SCRAPPER_URL = "%s://%s:%s" % ("http" if DEBUG else "https", SCRAPPER_HOST, SCRAPPER_PORT)
