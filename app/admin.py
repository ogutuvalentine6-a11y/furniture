from flask import (Blueprint, render_template, request, flash,
                   redirect, url_for)
from flask_login import login_required
from .extensions import db
from .models import Product, Category, Order, Customer, ContactMessage
from .utils import slugify
from . import team as team_mod
from pathlib import Path
from flask import current_app

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
VALID_STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")


@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "pending_orders": Order.query.filter_by(status="pending").count(),
        "customers": Customer.query.count(),
        "messages": ContactMessage.query.count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders)


@admin_bp.route("/products")
@login_required
def products():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=items)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def product_new():
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        data = _product_form_data()
        if not data["name"]:
            flash("Name is required.", "danger")
        elif not data["category_id"]:
            flash("Category is required.", "danger")
        else:
            p = Product(**data)
            base_slug = slugify(data["name"]) or "product"
            slug, n = base_slug, 1
            while Product.query.filter_by(slug=slug).first():
                n += 1
                slug = f"{base_slug}-{n}"
            p.slug = slug
            db.session.add(p)
            db.session.commit()
            flash("Product created.", "success")
            return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", product=None, categories=categories)


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def product_edit(pid):
    p = Product.query.get_or_404(pid)
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        data = _product_form_data()
        if not data["name"]:
            flash("Name is required.", "danger")
        else:
            for k, v in data.items():
                setattr(p, k, v)
            if p.slug != slugify(data["name"]):
                base_slug = slugify(data["name"]) or p.slug
                slug, n = base_slug, 1
                while Product.query.filter(Product.slug == slug,
                                            Product.id != p.id).first():
                    n += 1
                    slug = f"{base_slug}-{n}"
                p.slug = slug
            db.session.commit()
            flash("Product updated.", "success")
            return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", product=p, categories=categories)


@admin_bp.route("/products/<int:pid>/delete", methods=["POST"])
@login_required
def product_delete(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))


@admin_bp.route("/orders")
@login_required
def orders():
    items = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=items)


@admin_bp.route("/orders/<int:oid>")
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template("admin/order_detail.html", order=order, statuses=VALID_STATUSES)


@admin_bp.route("/orders/<int:oid>/status", methods=["POST"])
@login_required
def order_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get("status")
    if new_status in VALID_STATUSES:
        order.status = new_status
        db.session.commit()
        flash("Order status updated.", "success")
    else:
        flash("Invalid status.", "danger")
    return redirect(url_for("admin.order_detail", oid=oid))


@admin_bp.route("/customers")
@login_required
def customers():
    items = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template("admin/customers.html", customers=items)


def _product_form_data():
    return {
        "name": (request.form.get("name") or "").strip(),
        "description": (request.form.get("description") or "").strip(),
        "price": request.form.get("price", type=float) or 0.0,
        "stock": request.form.get("stock", type=int) or 0,
        "image": (request.form.get("image") or "").strip(),
        "colors": (request.form.get("colors") or "").strip(),
        "dimensions": (request.form.get("dimensions") or "").strip(),
        "material": (request.form.get("material") or "").strip(),
        "is_featured": bool(request.form.get("is_featured")),
        "is_bestseller": bool(request.form.get("is_bestseller")),
        "is_new": bool(request.form.get("is_new")),
        "category_id": request.form.get("category_id", type=int),
    }

@admin_bp.route("/team")
@login_required
def team_admin():
    return render_template("admin/team.html", members=team_mod.get_all())


@admin_bp.route("/team/upload", methods=["POST"])
@login_required
def team_upload():
    member_id = request.form.get("member_id", "").strip()
    file = request.files.get("photo")
    if not member_id or not file or not file.filename:
        flash("No file selected.", "danger")
        return redirect(url_for("admin.team_admin"))
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        flash("Only jpg, jpeg, png, webp allowed.", "danger")
        return redirect(url_for("admin.team_admin"))
    photo_dir = Path(current_app.static_folder) / "images" / "team"
    photo_dir.mkdir(parents=True, exist_ok=True)
    for old_ext in ("jpg", "jpeg", "png", "webp"):
        old = photo_dir / f"{member_id}.{old_ext}"
        if old.exists():
            old.unlink()
    file.save(photo_dir / f"{member_id}.{ext}")
    flash(f"Photo uploaded for {member_id}.", "success")
    return redirect(url_for("admin.team_admin"))


@admin_bp.route("/team/delete", methods=["POST"])
@login_required
def team_delete_photo():
    member_id = request.form.get("member_id", "").strip()
    photo_dir = Path(current_app.static_folder) / "images" / "team"
    removed = False
    for ext in ("jpg", "jpeg", "png", "webp"):
        f = photo_dir / f"{member_id}.{ext}"
        if f.exists():
            f.unlink()
            removed = True
    flash("Photo removed." if removed else "No photo to remove.", "info")
    return redirect(url_for("admin.team_admin"))

