from flask import Flask, render_template, url_for, request
from sqlalchemy import func, select

from webapp.models import Category, Good, Price
from webapp.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        current_category = request.args.get('category', None, type=str)
        page = request.args.get('page', 1, type=int)
        per_page = app.config['OFFSET']
        if current_category:
            page_title = current_category.capitalize()
            category_id = db.session.query(Category.id).filter(Category.name == current_category).scalar()
            query = db.session.query(Good).filter(Good.category_id == category_id)
            pagination = query.paginate(page=page, per_page=per_page)
            return render_template('index.html', page_title=page_title, page=page, products=pagination.items, total_pages=pagination.pages, categories=app.config['CATEGORIES'], current_category=current_category)
        else:
            page_title = 'Categories'
            query = db.session.query(Good)
            pagination = query.paginate(page=page, per_page=per_page)
            return render_template('index.html', page_title=page_title, page=page, products=pagination.items, total_pages=pagination.pages, categories=app.config['CATEGORIES'])
    
    @app.route('/product/<int:product_id>')
    def product(product_id):
        subq = select(Price.good_id, func.max(Price.date).label("date")).where(Price.good_id == 1).group_by("good_id").subquery()
        subq2 = select(Price.value, Price.value_discount, Price.date, Price.good_id).join(subq, (Price.good_id == subq.c.good_id) & (Price.date == subq.c.date)).subquery()
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