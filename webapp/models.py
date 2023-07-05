from webapp.db import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'

class Country(db.Model):
    __tablename__ = 'counrties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Country {self.name}>'

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    symbol = db.Column(db.String, unique=True, nullable=True)

    def __repr__(self):
        return f'<Currency {self.name} {self.symbol}>'  

class Shop(db.Model):
    __tablename__ = 'shops'

    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey(Country.id), index=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    name = db.Column(db.String, unique=True, nullable=False)
    site_link = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Shop {self.name}>'      
         
class Good(db.Model):
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id), index=True, nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey(Shop.id), index=True, nullable=False)
    units = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    image = db.Column(db.String, nullable=True)
    link = db.Column(db.String, unique=True, nullable=True)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Good {self.name}>'    

class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    currency_id = db.Column(db.Integer, db.ForeignKey(Currency.id), index=True, nullable=False)
    good_id = db.Column(db.Integer, db.ForeignKey(Good.id), index=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    value_discount = db.Column(db.Float, nullable=True)
    value = db.Column(db.Float)

    def __repr__(self):
        return f'<Price {self.value}>'  