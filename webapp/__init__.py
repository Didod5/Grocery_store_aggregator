from flask import Flask, render_template, url_for, request
from sqlalchemy import func, select

from webapp.models import Good, Price
from webapp.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        page_title = 'Categories'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 24, type=int)
        total_pages = (db.session.query(func.count(Good.id)).scalar() + per_page - 1) // per_page
        offset = (page - 1) * per_page
        goods = Good.query.limit(per_page).offset(offset).all()
        prices = Price.query.all()
        return render_template('index.html', page_title=page_title, page=page, products=goods, total_pages=total_pages)
    
    @app.route('/product/<int:product_id>')
    def product(product_id):
        subq = select(Price.good_id, func.max(Price.date)).where(Price.good_id == product_id).group_by("good_id").subquery()
        subq2 = select(Price.value, Price.value_discount, Price.date, Price.good_id).join(subq, Price.good_id == subq.c.good_id and Price.date == subq.c.date).subquery()
        result = db.session.execute(
            select(
                    Good.name, Good.description, Good.image, Good.rating, Good.units, subq2.c.value, subq2.c.value_discount, subq2.c.date
            ).join(subq2, Good.id == subq2.c.good_id)
        ).first()
        if result:
            product = {
                'date': result.date,
                'description': result.description,
                'image': result.image,
                'name': result.name,
                'price': result.value,
                'price_discount': result.value_discount,
                'rating': result.rating,
                'units': result.units
            }
            return render_template('product.html', page_title=product['name'], product=product)
        return "404"

    return app
