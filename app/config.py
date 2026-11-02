import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    _db_path = BASE_DIR / "instance" / "furniturehub.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{_db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Currency
    CURRENCY = "KES"
    CURRENCY_SYMBOL = "KSh"

    # Delivery
    FREE_DELIVERY_THRESHOLD = 65000   # KSh
    DELIVERY_FEE = 3500               # KSh
