from flask import (Blueprint, render_template, request, session,
                   flash, redirect, url_for, current_app)
from .extensions import db
from .models import Customer, Order, OrderItem
from .utils import cart_items_from_session, generate_reference, is_valid_email

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout")


@checkout_bp.route("/", methods=["GET", "POST"])
def index():
    cart = session.get("cart", {})
    items, subtotal = cart_items_from_session(cart)
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view"))

    threshold = current_app.config["FREE_DELIVERY_THRESHOLD"]
    fee = current_app.config["DELIVERY_FEE"]
    delivery = 0 if subtotal >= threshold else fee
    total = subtotal + delivery

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        address = (request.form.get("address") or "").strip()
        payment = request.form.get("payment_method", "cod")

        errors = []
        if not name: errors.append("Name is required.")
        if not is_valid_email(email): errors.append("Valid email is required.")
        if not phone: errors.append("Phone is required.")
        if not address: errors.append("Delivery address is required.")
        if payment not in ("cod", "card_placeholder"): errors.append("Invalid payment method.")

        if errors:
            for e in errors: flash(e, "danger")
        else:
            customer = Customer.query.filter_by(email=email).first()
            if not customer:
                customer = Customer(name=name, email=email, phone=phone, address=address)
                db.session.add(customer)
                db.session.flush()
            else:
                customer.name = name
                customer.phone = phone
                customer.address = address

            order = Order(reference=generate_reference(), customer_id=customer.id,
                          total=total, status="pending", payment_method=payment,
                          delivery_address=address)
            db.session.add(order)
            db.session.flush()

            for item in items:
                p = item["product"]
                if item["quantity"] > p.stock:
                    flash(f"Sorry, only {p.stock} of {p.name} available.", "danger")
                    db.session.rollback()
                    return redirect(url_for("cart.view"))
                p.stock -= item["quantity"]
                db.session.add(OrderItem(order_id=order.id, product_id=p.id,
                                         product_name=p.name, unit_price=p.price,
                                         quantity=item["quantity"],
                                         line_total=item["line_total"]))

            db.session.commit()
            session["cart"] = {}
            session["last_order_ref"] = order.reference
            session.modified = True
            return redirect(url_for("checkout.success"))

    return render_template("checkout.html", items=items, subtotal=subtotal,
                           delivery=delivery, total=total)


@checkout_bp.route("/success")
def success():
    ref = session.get("last_order_ref")
    if not ref:
        return redirect(url_for("main.index"))
    order = Order.query.filter_by(reference=ref).first()
    return render_template("order_success.html", order=order)
