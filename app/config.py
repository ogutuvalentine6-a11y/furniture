import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# On Render, /opt/render/project is ephemeral; use /tmp for the DB
import os as _os
if _os.environ.get("RENDER"):
    INSTANCE_DIR = Path("/tmp/instance")
else:
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
