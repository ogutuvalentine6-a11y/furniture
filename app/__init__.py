from flask import Flask, session
from .config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def inject_globals():
        cart = session.get("cart", {}) or {}
        count = sum(int(v) for v in cart.values() if str(v).isdigit())
        return {
            "cart_count": count,
            "free_delivery_threshold": app.config["FREE_DELIVERY_THRESHOLD"],
            "delivery_fee": app.config["DELIVERY_FEE"],
            "currency_symbol": app.config["CURRENCY_SYMBOL"],
        }

    from .main import main_bp
    from .auth import auth_bp
    from .cart import cart_bp
    from .checkout import checkout_bp
    from .admin import admin_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    from .utils import format_price
    app.jinja_env.filters["money"] = format_price

    def _small_img(url, w=500):
        if not url:
            return ""
        # Downsize Unsplash URLs on the fly (keep hero at full size)
        if "images.unsplash.com" in url:
            url = re.sub(r"w=\d+", f"w={w}", url)
        return url

    import re
    app.jinja_env.filters["small"] = _small_img

    with app.app_context():
        db.create_all()

    return app
