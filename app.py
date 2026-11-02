"""WSGI entry point for Render / gunicorn `app:app` default."""
import os
from app import create_app

# Ensure instance/ exists (Render free tier uses ephemeral /tmp)
os.makedirs("instance", exist_ok=True)

app = create_app()
