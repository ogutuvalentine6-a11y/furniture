import re
import secrets
from .models import Product

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(v):
    return bool(EMAIL_RE.match(v or ""))

def slugify(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

def generate_reference():
    return "FH-" + secrets.token_hex(4).upper()

def cart_items_from_session(session_cart):
    items, total = [], 0.0
    if not session_cart:
        return items, total
    try:
        ids = [int(k) for k in session_cart.keys()]
    except (TypeError, ValueError):
        return items, total
    products = {p.id: p for p in Product.query.filter(Product.id.in_(ids)).all()}
    for pid_str, qty in session_cart.items():
        p = products.get(int(pid_str))
        if not p:
            continue
        try:
            q = int(qty)
        except (TypeError, ValueError):
            continue
        if q <= 0:
            continue
        line = round(p.price * q, 2)
        items.append({"product": p, "quantity": q, "line_total": line})
        total += line
    return items, round(total, 2)

def format_price(v):
    """Format a number as Kenya Shillings: KSh 168,000"""
    try:
        n = float(v)
        # whole shillings only — no cents
        return f"KSh {n:,.0f}"
    except (TypeError, ValueError):
        return "KSh 0"
