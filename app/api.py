from flask import Blueprint, jsonify, request, session
from .models import Product, Category
from .utils import cart_items_from_session

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/products")
def products():
    q = (request.args.get("q") or "").strip()
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    items = query.limit(20).all()
    return jsonify([{
        "id": p.id, "name": p.name, "slug": p.slug, "price": p.price,
        "stock": p.stock, "image": p.image,
        "category": p.category.name if p.category else None,
    } for p in items])


@api_bp.route("/categories")
def categories():
    return jsonify([{"id": c.id, "name": c.name, "slug": c.slug}
                    for c in Category.query.all()])


@api_bp.route("/cart")
def cart():
    items, total = cart_items_from_session(session.get("cart", {}))
    return jsonify({
        "items": [{
            "product_id": it["product"].id,
            "name":       it["product"].name,
            "slug":       it["product"].slug,
            "price":      it["product"].price,
            "image":      it["product"].image,
            "quantity":   it["quantity"],
            "line_total": it["line_total"],
        } for it in items],
        "total": total,
        "count": sum(it["quantity"] for it in items),
    })
