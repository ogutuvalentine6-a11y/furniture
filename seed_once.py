"""Seed the DB only if it's empty. Idempotent."""
from app import create_app
from app.extensions import db
from app.models import Category
from seed import run

app = create_app()
with app.app_context():
    db.create_all()
    if Category.query.count() == 0:
        print("Empty DB — seeding...")
        run()
    else:
        print("DB already seeded — skipping")
