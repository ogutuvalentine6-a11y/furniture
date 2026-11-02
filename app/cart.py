from flask import (Blueprint, session, request, redirect, url_for,
                   render_template, flash)
from .models import Product
from .utils import cart_items_from_session

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


def _cart():
    return session.setdefault("cart", {})


@cart_bp.route("/")
def view():
    items, total = cart_items_from_session(_cart())
    return render_template("cart.html", items=items, total=total)


@cart_bp.route("/add", methods=["POST"])
def add():
    pid = request.form.get("product_id", type=int)
    qty = request.form.get("quantity", 1, type=int) or 1
    if not pid or qty <= 0:
        flash("Invalid product or quantity.", "danger")
        return redirect(request.referrer or url_for("main.shop"))
    p = Product.query.get(pid)
    if not p:
        flash("Product not found.", "danger")
        return redirect(url_for("main.shop"))
    if qty > p.stock:
        qty = p.stock
    if qty <= 0:
        flash("This item is out of stock.", "danger")
        return redirect(request.referrer or url_for("main.shop"))
    cart = _cart()
    cart[str(pid)] = cart.get(str(pid), 0) + qty
    session["cart"] = cart
    session.modified = True
    flash(f"Added \u201c{p.name}\u201d to your cart.", "success")
    return redirect(request.referrer or url_for("cart.view"))


@cart_bp.route("/update", methods=["POST"])
def update():
    pid = request.form.get("product_id")
    qty = request.form.get("quantity", type=int)
    cart = _cart()
    if pid in cart:
        if qty is None or qty <= 0:
            del cart[pid]
        else:
            p = Product.query.get(int(pid))
            if p and qty > p.stock:
                qty = p.stock
            cart[pid] = qty
        session["cart"] = cart
        session.modified = True
    return redirect(url_for("cart.view"))


@cart_bp.route("/remove", methods=["POST"])
def remove():
    pid = request.form.get("product_id")
    cart = _cart()
    cart.pop(pid, None)
    session["cart"] = cart
    session.modified = True
    flash("Item removed.", "info")
    return redirect(url_for("cart.view"))


@cart_bp.route("/clear", methods=["POST"])
def clear():
    session["cart"] = {}
    session.modified = True
    flash("Cart cleared.", "info")
    return redirect(url_for("cart.view"))
