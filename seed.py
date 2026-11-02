"""Seed FurnitureHub with categories, demo products and an admin user."""
from app import create_app
from app.extensions import db
from app.models import Category, Product, AdminUser
from app.utils import slugify

CATEGORIES = ["Living Room", "Bedroom", "Dining Room", "Office",
              "Outdoor Furniture", "Lighting", "Accessories"]

PRODUCTS = [
    ("Aria Sofa", "Living Room", 169000.0, 8,
     "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=80",
     "Ivory, Charcoal, Oak", "220 x 95 x 80 cm", "Oak frame, linen upholstery",
     True, True, False, "A soft three-seater sofa with clean lines and deep, cloud-like cushions."),
    ("Nordic Armchair", "Living Room", 71500.0, 14,
     "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=900&q=80",
     "Beige, Charcoal", "75 x 80 x 90 cm", "Solid oak, wool blend",
     True, False, True, "An armchair that balances Scandinavian restraint with everyday comfort."),
    ("Halo Coffee Table", "Living Room", 45500.0, 20,
     "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=900&q=80",
     "Oak, Walnut", "110 x 60 x 40 cm", "Solid oak, tempered glass",
     False, True, False, "A round coffee table with a tempered-glass top and slim oak base."),
    ("Linen Bed Frame", "Bedroom", 117000.0, 6,
     "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80",
     "Ivory, Sand", "200 x 180 x 100 cm", "Pine core, linen headboard",
     True, False, True, "A king-size bed frame with a softly upholstered headboard."),
    ("Marlow Nightstand", "Bedroom", 28500.0, 22,
     "https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=900&q=80",
     "Oak, White", "50 x 40 x 55 cm", "Oak veneer",
     False, False, True, "A two-drawer nightstand finished with antique brass pulls."),
    ("Ember Dresser", "Bedroom", 95000.0, 9,
     "https://images.unsplash.com/photo-1616046229478-9901c5536a45?w=900&q=80",
     "Walnut", "140 x 45 x 80 cm", "Solid walnut",
     False, True, False, "A six-drawer dresser with a warm walnut finish and tapered legs."),
    ("Hearth Dining Table", "Dining Room", 156000.0, 5,
     "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=900&q=80",
     "Oak, Charcoal", "180 x 90 x 75 cm", "Solid oak",
     True, True, False, "A robust six-seater table built from solid oak and finished by hand."),
    ("Dune Dining Chair", "Dining Room", 19500.0, 40,
     "https://images.unsplash.com/photo-1503602642458-232111445657?w=900&q=80",
     "Beige, Charcoal", "50 x 55 x 80 cm", "Oak, woven seat",
     False, False, True, "A stackable chair with a woven seat and softly curved back."),
    ("Atlas Desk", "Office", 84500.0, 12,
     "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=900&q=80",
     "Oak, Charcoal", "140 x 70 x 75 cm", "Oak, powder-coated steel",
     True, False, False, "A clean-lined desk with a discreet cable-management tray."),
    ("Orbit Office Chair", "Office", 52000.0, 18,
     "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=900&q=80",
     "Charcoal, Beige", "60 x 60 x 95 cm", "Mesh, aluminium",
     False, True, False, "An ergonomic task chair with adjustable arms and a breathable mesh back."),
    ("Sol Patio Set", "Outdoor Furniture", 117000.0, 4,
     "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=900&q=80",
     "Sand", "200 x 80 x 75 cm", "Teak, weatherproof weave",
     True, False, True, "A three-piece set built for the terrace, made from teak and weatherproof weave."),
    ("Halo Floor Lamp", "Lighting", 24500.0, 25,
     "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900&q=80",
     "Charcoal, Brass", "30 x 30 x 160 cm", "Steel, linen shade",
     False, False, True, "A slim floor lamp with a linen shade that casts a warm, even glow."),
    ("Aster Pendant Light", "Lighting", 17000.0, 30,
     "https://images.unsplash.com/photo-1543198126-a8ad8e47fb22?w=900&q=80",
     "Brass, Black", "25 x 25 x 30 cm", "Steel, brass",
     False, True, False, "A pendant that casts a warm pool of light over dining tables and counters."),
    ("Mira Vase", "Accessories", 7500.0, 60,
     "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=900&q=80",
     "Sand", "15 x 15 x 25 cm", "Hand-thrown ceramic",
     False, False, True, "A hand-thrown ceramic vase with a softly matte glaze."),
    ("Woven Rug", "Accessories", 32500.0, 15,
     "https://images.unsplash.com/photo-1600166898405-da9535204843?w=900&q=80",
     "Beige, Ivory", "200 x 150 cm", "Wool, cotton",
     False, True, False, "A softly textured wool rug that grounds a room without overwhelming it."),
]


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        if Category.query.count() == 0:
            for name in CATEGORIES:
                db.session.add(Category(name=name, slug=slugify(name)))
            db.session.commit()
            print(f"  + {len(CATEGORIES)} categories")

        if Product.query.count() == 0:
            cats = {c.name: c for c in Category.query.all()}
            for row in PRODUCTS:
                (name, cat, price, stock, img, colors, dims, mat,
                 feat, best, new, desc) = row
                db.session.add(Product(
                    name=name, slug=slugify(name), description=desc,
                    price=price, stock=stock, image=img, colors=colors,
                    dimensions=dims, material=mat, is_featured=feat,
                    is_bestseller=best, is_new=new,
                    category_id=cats[cat].id,
                ))
            db.session.commit()
            print(f"  + {len(PRODUCTS)} products")

        if not AdminUser.query.filter_by(username="admin").first():
            u = AdminUser(username="admin")
            u.set_password("admin123")
            db.session.add(u)
            db.session.commit()
            print("  + admin user -> admin / admin123")


if __name__ == "__main__":
    print("Seeding FurnitureHub...")
    run()
    print("Done.")
