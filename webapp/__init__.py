from flask import Flask, render_template, url_for, request
from webapp.models import Good, Price
from webapp.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        page_title = 'Aggregator'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        offset = (page - 1) * per_page
        goods = Good.query.limit(per_page).offset(offset).all()
        prices = Price.query.all()
        return render_template('index.html', page_title=page_title, page=page, products=goods)
    
    @app.route('/product/<int:product_id>')
    def product(product_id):  
        return render_template('product.html')

    return app