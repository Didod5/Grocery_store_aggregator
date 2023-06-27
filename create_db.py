from webapp import db, create_app
from webapp.models import Category, Country, Currency, Price, Shop, Unit, Good

app=create_app()
with app.app_context():
    db.create_all()