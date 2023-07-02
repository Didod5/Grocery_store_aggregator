from flask import Flask, render_template, url_for

from webapp.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        page_title = 'Aggregator'
        return render_template('index.html', page_title=page_title)
    
    @app.route('/product/<int:product_id>')
    def product(product_id):
        
        # здесь надо вытаскивать данные из базы
        product_data = {
            'name': '',
            'description': '',
            'price': '',
            'img_path': ''
        }
        
        return render_template('product.html', product=product_data)

    return app