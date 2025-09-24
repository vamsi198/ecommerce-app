from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------- Database Config --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@db:5432/ecommerce_db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- Models --------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

# -------------------- Routes --------------------
@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    session.modified = True
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    if "cart" not in session or len(session["cart"]) == 0:
        return render_template("cart.html", products=[])
    cart_products = Product.query.filter(Product.id.in_(session["cart"])).all()
    return render_template("cart.html", products=cart_products)

@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    return render_template("checkout.html")

# -------------------- Init DB with sample products --------------------
def setup_db():
    """Initialize database and add sample products if empty."""
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            db.session.add_all([
                Product(name="Laptop", price=700),
                Product(name="Phone", price=300),
                Product(name="Headphones", price=50),
            ])
            db.session.commit()

# -------------------- Run --------------------
if __name__ == "__main__":
    setup_db()  # Run once when app starts
    app.run(host="0.0.0.0", port=5000)
