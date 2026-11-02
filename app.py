"""WSGI entry point — works with Render's default `gunicorn app:app`."""
import os
from pathlib import Path

# Ensure instance/ exists (Render free tier ephemeral filesystem)
BASE = Path(__file__).resolve().parent
os.makedirs(BASE / "instance", exist_ok=True)

from app import create_app

app = create_app()

# Auto-seed on first startup if DB is empty (idempotent, safe to run every deploy)
with app.app_context():
    from app.extensions import db
    from app.models import Category
    db.create_all()
    if Category.query.count() == 0:
        try:
            print("🌱 Empty database — auto-seeding...")
            from seed import run as seed_run
            seed_run()
            print("✅ Seed complete")
        except Exception as e:
            print(f"⚠️  Auto-seed failed (non-fatal): {e}")
    else:
        print(f"✓ Database already has {Category.query.count()} categories — skipping seed")
