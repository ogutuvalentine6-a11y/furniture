"""Group 11 team data + photo detection."""
from pathlib import Path

PHOTO_DIR = Path(__file__).parent / "static" / "images" / "team"
PHOTO_EXTS = ("jpg", "jpeg", "png", "webp")

TEAM = [
    {
        "id": "brian",
        "name": "Brian Ouma Ochieng",
        "reg": "PA106/G/28812/25",
        "role": "Founder & Lead Full-Stack Engineer",
        "short_role": "Founder & Lead",
        "initials": "BO",
        "bio": "As founder and lead engineer, Brian architected FurnitureHub from the ground up — from the Flask application factory to the deployment pipeline on Render. He specialises in full-stack systems, cloud deployment and technical leadership. His approach pairs rigorous engineering with a designer's eye for detail, and he is passionate about mentoring the next generation of developers.",
        "contribution": "System architecture, all six Flask blueprints, authentication layer, deployment pipeline (Render + GitHub), technical coordination, and the Group 11 vision.",
        "project_vision": "Brian's vision for FurnitureHub was simple: build a commerce platform that feels as considered as the furniture it sells. Every design decision — from the ivory-and-charcoal palette to the FH-XXXXXXXX order references — was shaped by his commitment to quality.",
        "skills": ["Python", "Flask", "SQLAlchemy", "Docker", "GitHub Actions", "Render", "Linux", "Technical Leadership"],
        "contact": {"phone": "0707810455", "email": "braianouma3@gmail.com"},
        "is_founder": True,
    },
    {
        "id": "ogutu",
        "name": "Ogutu Valentine Otieno",
        "reg": "PA106/G/28813/25",
        "role": "Senior Backend Engineer",
        "short_role": "Backend",
        "initials": "OV",
        "bio": "Valentine specialises in backend architecture and API design. He designed the routing layer that powers every product, order and authentication flow on FurnitureHub. His focus is on reliability — every endpoint is validated, every session is secure, and every error is handled gracefully.",
        "contribution": "All API route handlers, session management, customer authentication, backend validation, order processing logic, security hardening.",
        "project_vision": "For Valentine, the backend is the invisible scaffold of great UX. Customers should never have to think about how it works — it should just work.",
        "skills": ["Python", "REST APIs", "Flask-Login", "Session Management", "Security", "SQLAlchemy"],
        "contact": {},
        "is_founder": False,
    },
    {
        "id": "kiprotich",
        "name": "Kiprotich Collins",
        "reg": "PA106/G/28814/25",
        "role": "Database Architect & DevOps",
        "short_role": "Database",
        "initials": "KC",
        "bio": "Collins designed the seven-table database schema that underpins FurnitureHub. He is passionate about data integrity, normalised design and query performance. He also owns the seed data pipeline that makes demo deployments reproducible across machines and environments.",
        "contribution": "Database schema, all SQLAlchemy ORM models, seed scripts, query optimisation, data relationships, integrity constraints.",
        "project_vision": "Collins believes a well-designed schema is the single highest-leverage decision in any backend project. Clean data models make everything else — routes, filters, admin tools — exponentially easier.",
        "skills": ["SQL", "SQLAlchemy", "Database Design", "Indexing", "Data Modeling", "DevOps"],
        "contact": {},
        "is_founder": False,
    },
    {
        "id": "elvine",
        "name": "Elvine Bala Adidwa",
        "reg": "PA106/G/28815/25",
        "role": "Senior UI/UX Engineer",
        "short_role": "UI/UX",
        "initials": "EB",
        "bio": "Elvine leads design at FurnitureHub. She created the premium visual language — the ivory-and-charcoal palette, the Playfair type pairing, the oak gradient accents, the motion system. Everything you see was shaped by her eye. She designs for clarity and delight in equal measure.",
        "contribution": "Design system, colour palette, typography pairing, micro-animations, accessibility, all public-facing templates, responsive layout strategy.",
        "project_vision": "Elvine's north star: the site should feel like walking into a beautifully curated furniture showroom — calm, warm, and inviting. Every pixel earns its place.",
        "skills": ["UI Design", "UX Research", "Tailwind CSS", "Design Systems", "Accessibility", "Figma"],
        "contact": {},
        "is_founder": False,
    },
    {
        "id": "oyier",
        "name": "Oyier Edward Hamilton",
        "reg": "PA106/G/28816/25",
        "role": "Frontend Engineer",
        "short_role": "Frontend",
        "initials": "OE",
        "bio": "Edward owns the interactive layer. The command palette (Ctrl+K), the slide-in cart drawer, the toast notifications, the animated counters, the scroll reveals — every micro-interaction on the site was built by his hand. He is meticulous about performance and smooth motion.",
        "contribution": "JavaScript interactions, cart drawer, command palette, toast system, scroll animations, floating admin FAB, product card tilt effects.",
        "project_vision": "Edward believes interactions should be effortless. Users shouldn't notice the JavaScript — they should just feel that everything responds instantly.",
        "skills": ["JavaScript", "DOM APIs", "CSS Animations", "Performance", "Responsive Design"],
        "contact": {},
        "is_founder": False,
    },
]


def get_photo(member_id):
    """Returns 'images/team/<id>.<ext>' if a photo exists, else None."""
    for ext in PHOTO_EXTS:
        if (PHOTO_DIR / f"{member_id}.{ext}").exists():
            return f"images/team/{member_id}.{ext}"
    return None


def with_photos(members):
    """Enrich members with photo URL (DB takes priority over filesystem)."""
    from .models import TeamPhoto
    from flask import url_for
    result = []
    for m in members:
        fs_path = get_photo(m["id"])
        has_db = TeamPhoto.query.filter_by(member_id=m["id"]).first() is not None
        if has_db:
            try:
                photo_url = url_for("main.team_photo", member_id=m["id"])
            except RuntimeError:
                photo_url = f"/team/photo/{m['id']}"
        elif fs_path:
            try:
                photo_url = url_for("static", filename=fs_path)
            except RuntimeError:
                photo_url = f"/static/{fs_path}"
        else:
            photo_url = None
        result.append({**m, "photo": fs_path, "photo_db": has_db, "photo_url": photo_url})
    return result


def get_all():
    return with_photos(TEAM)


def get_one(member_id):
    for m in TEAM:
        if m["id"] == member_id:
            return with_photos([m])[0]
    return None


def get_neighbors(member_id):
    ids = [m["id"] for m in TEAM]
    if member_id not in ids:
        return None, None
    i = ids.index(member_id)
    return get_one(ids[(i - 1) % len(ids)]), get_one(ids[(i + 1) % len(ids)])
