from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db, login_manager


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(400), default="")
    colors = db.Column(db.String(200), default="")
    dimensions = db.Column(db.String(200), default="")
    material = db.Column(db.String(120), default="")
    is_featured = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", back_populates="products")

    @property
    def color_list(self):
        return [c.strip() for c in (self.colors or "").split(",") if c.strip()]

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock < 5


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), default="")
    address = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship("Order", back_populates="customer")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(32), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)  # includes delivery
    status = db.Column(db.String(30), default="pending")
    payment_method = db.Column(db.String(40), default="cod")
    delivery_address = db.Column(db.Text, default="")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Float, nullable=False)
    order = db.relationship("Order", back_populates="items")


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), default="")
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamPhoto(db.Model):
    """Team member photo uploaded from phones (survives between deploys)."""
    __tablename__ = "team_photos"
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(40), unique=True, nullable=False, index=True)
    data = db.Column(db.LargeBinary, nullable=False)
    mime = db.Column(db.String(40), default="image/jpeg")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))
