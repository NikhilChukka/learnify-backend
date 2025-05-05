# app/core/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
MONGO_DETAILS = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
# print(MONGO_DETAILS, SECRET_KEY, end="\n")