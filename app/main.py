from flask import (Blueprint, render_template, request, flash, redirect,
                   url_for, jsonify)
from sqlalchemy import or_
from .extensions import db
from .models import (Product, Category, ContactMessage,
                     Customer, Order, NewsletterSubscriber)
from .utils import is_valid_email
from . import team as team_mod

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = Product.query.filter_by(is_featured=True).limit(4).all()
    bestsellers = Product.query.filter_by(is_bestseller=True).limit(4).all()
    new_arrivals = (Product.query.filter_by(is_new=True)
                    .order_by(Product.created_at.desc()).limit(4).all())
    categories = Category.query.order_by(Category.name).all()
    stats = {
        "products": Product.query.count(),
        "categories": Category.query.count(),
        "customers": Customer.query.count(),
        "orders": Order.query.count(),
    }
    return render_template("index.html",
                           featured=featured, bestsellers=bestsellers,
                           new_arrivals=new_arrivals, categories=categories,
                           stats=stats, members=team_mod.get_all())


@main_bp.route("/shop")
def shop():
    q = (request.args.get("q") or "").strip()
    cat_slug = (request.args.get("category") or "").strip()
    min_p = request.args.get("min_price", type=float)
    max_p = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "newest")

    query = Product.query
    if q:
        query = query.filter(or_(Product.name.ilike(f"%{q}%"),
                                 Product.description.ilike(f"%{q}%")))
    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    if min_p is not None:
        query = query.filter(Product.price >= min_p)
    if max_p is not None:
        query = query.filter(Product.price <= max_p)

    sort_map = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "name": Product.name.asc(),
    }
    query = query.order_by(sort_map.get(sort, Product.created_at.desc()))

    products = query.all()
    categories = Category.query.order_by(Category.name).all()
    return render_template("shop.html", products=products, categories=categories,
                           q=q, cat_slug=cat_slug, min_p=min_p, max_p=max_p, sort=sort)


@main_bp.route("/product/<slug>")
def product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    related = (Product.query
               .filter(Product.category_id == p.category_id, Product.id != p.id)
               .limit(4).all())
    return render_template("product.html", product=p, related=related)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()
        if not name or not email or not message:
            flash("Name, email and message are required.", "danger")
        elif not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
        else:
            db.session.add(ContactMessage(name=name, email=email,
                                          subject=subject, message=message))
            db.session.commit()
            flash("Thanks — we'll be in touch shortly.", "success")
            return redirect(url_for("main.contact"))
    return render_template("contact.html")


@main_bp.route("/team")
def team_list():
    return render_template("team.html", members=team_mod.get_all())


@main_bp.route("/team/<member_id>")
def team_member(member_id):
    member = team_mod.get_one(member_id)
    if not member:
        from flask import abort
        abort(404)
    prev_m, next_m = team_mod.get_neighbors(member_id)
    return render_template("team_member.html", member=member,
                           prev_member=prev_m, next_member=next_m)


@main_bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    if not is_valid_email(email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({"ok": True, "message": "You're already subscribed. Thanks!"})
    db.session.add(NewsletterSubscriber(email=email))
    db.session.commit()
    return jsonify({"ok": True, "message": "Thanks for subscribing!"})
