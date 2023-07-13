from flask import Flask, render_template, url_for, request
import math
from sqlalchemy import func, select, desc

from webapp.models import Category, Good, Price
from webapp.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        current_category = request.args.get('category', None, type=str)
        search_text = request.args.get('q', None, type=str)
        page = request.args.get('page', 1, type=int)
        per_page = app.config['OFFSET']
        if search_text:
            page_title = 'Search'
            total_pages = math.ceil((db.session.scalar(
                select(func.count()).where(Good.name.ilike(f'%{search_text}%'))
            ))/per_page)
            results = db.session.execute(
                select(Good.id, Good.name, Good.description, Good.image, Good.rating, Good.units).where(Good.name.ilike(f'%{search_text}%')).limit(per_page).offset((page-1)*per_page)
            ).fetchall()
            if results:
                products = []
                for object in results:
                    product = {
                        'id': object.id,
                        'description': object.description,
                        'image': object.image,
                        'name': object.name,
                        'rating': object.rating,
                        'units': object.units
                    }
                    products.append(product)
                return render_template('index.html', page_title=page_title, page=page, products=products, total_pages=total_pages, categories=app.config['CATEGORIES'], q=search_text)
            else:
                return render_template('index.html', page_title=page_title, categories=app.config['CATEGORIES'], is_unsuccessful_search = True)

        else:
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
        good = db.session.execute(select(Good.name, Good.description, Good.image, Good.rating, Good.units).where(Good.id == product_id)).first()
        if good:
            product = {
                'description': good.description,
                'image': good.image,
                'name': good.name,
                'rating': good.rating,
                'units': good.units
            }
            prices = db.session.execute(select(Price.date, Price.value, Price.value_discount).where(Price.good_id == product_id).order_by(desc(Price.date))).fetchall()
            if prices:
                costs = []
                for object in prices:
                    cost = {
                        'value': object.value,
                        'value_discount': object.value_discount,
                        'date': object.date  
                    }
                    costs.append(cost)
                current_cost = costs[0]
                if len(costs) > 1:
                    return render_template('product.html', page_title=product['name'], product=product, costs=costs, current_cost=current_cost)
                else:
                    return render_template('product.html', page_title=product['name'], product=product, current_cost=current_cost)
            return render_template('product.html', page_title=product['name'], product=product)
        return "404"

    return app