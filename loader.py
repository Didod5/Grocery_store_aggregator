from datetime import date

import requests
from sqlalchemy import insert

import settings
from webapp import create_app
from webapp.db import db
from webapp.models import Category, Country, Currency, Price, Shop, Good

def get_number_of_pages_by_category(category, url, params):
    params['category'] = category
    params['page'] = 1
    params['url'] = category

    try:
        result = requests.get(url, params=params)
        result.raise_for_status()
        goods = result.json() 
        if 'layouts' in goods['data']['page']:
            try:
                final_goods = next((item for item in goods['data']['page']['layouts'] if item['name'] == 'ProductCollection'), None)
                if final_goods:
                    return final_goods['value']['collection']['pagination']['total_pages']
            except(KeyError, TypeError):
                return False
    except (requests.RequestException, ValueError):
        return False
    return False   

def get_goods_page_by_category(category, url, params, page_num):
    params['category'] = category
    params['page'] = page_num
    params['url'] = category
  
    try:
        result = requests.get(url, params=params)
        result.raise_for_status()
        goods = result.json() 
        if 'layouts' in goods['data']['page']:
            try:
                final_goods = next((item for item in goods['data']['page']['layouts'] if item['name'] == 'ProductCollection'), None)
                if final_goods:
                    return final_goods['value']['collection']['product']
            except(KeyError, TypeError):
                return False
    except (requests.RequestException, ValueError):
        return False
    return False

def extract_good_data(good, category):
    final_good = {}

    final_good['shop_name'] = settings.SHOP_NAME
    final_good['shop_country'] = settings.SHOP_COUNTRY
    final_good['shop_description'] = settings.SHOP_DESCRIPTION
    final_good['shop_link'] = settings.SHOP_LINK

    final_good['currency_name'] = 'SGD'
    final_good['currency_symbol'] = 'S$'

    final_good['category_name'] = category

    if 'mrp' in good['storeSpecificData'][0]:
        final_good['price'] = good['storeSpecificData'][0]['mrp']
    if 'offers' in good:
        final_good['price_discount'] = good['offers'][0]['price']
    final_good['price_date'] = date.today()

    if 'name' in good:
        final_good['name'] = good['name']
    if 'DisplayUnit' in good['metaData']:
        final_good['units'] = good['metaData']['DisplayUnit']
    if 'images' in good:
        final_good['image'] = good['images'][0]
    if 'slug' in good:
        final_good['link'] = settings.PRODUCT_LINK + good['slug']
    if 'averageDisplay' in good['reviews']['statistics']:
        final_good['rating'] = good['reviews']['statistics']['averageDisplay']
    if 'description' in good:
        final_good['description'] = good['description']

    return final_good
    
def get_goods_by_category(category, url, params):
    page_number = get_number_of_pages_by_category(category, url, params)
    if page_number:
        category_items = []
        for i in range(page_number):
            goods = get_goods_page_by_category(category, url, params, i+1)
            if goods:
                for good in goods:
                    category_items.append(extract_good_data(good, category))
        if len(category_items) < 1:
            return False
        return category_items
    return False

def save_category(category_name):
    category = {'name': category_name}
    category_id = db.session.scalar(
        insert(Category).returning(Category.id), category
    )
    db.session.commit()
    category["id"] = category_id
    return category

def save_currencies(data):
    processed = []
    unique_currencies = []
    for row in data:
        if row['currency_name'] not in processed:
            currency = {
                'name': row['currency_name'],
                'symbol': row['currency_symbol']
            }
            unique_currencies.append(currency)
            processed.append(currency['name'])
    currency_ids = db.session.scalars(
        insert(Currency).returning(Currency.id, sort_by_parameter_order=True), unique_currencies
    )
    db.session.commit()
    for currency_id, currency in zip(currency_ids, unique_currencies):
        currency["id"] = currency_id
    return unique_currencies

def save_countries(data):
    processed = []
    unique_countries = []
    for row in data:
        if row['shop_country'] not in processed:
            counrty = {'name': row['shop_country']}
            unique_countries.append(counrty)
            processed.append(counrty['name'])
    counrty_ids = db.session.scalars(
        insert(Country).returning(Country.id, sort_by_parameter_order=True), unique_countries
    )
    db.session.commit()
    for counrty_id, counrty in zip(counrty_ids, unique_countries):
        counrty["id"] = counrty_id
    return unique_countries

def get_counrty_by_id(countries, country_name):
    for country in countries:
        if country['name'] == country_name:
            return country['id']

def save_shops(data, countries):
    processed = []
    unique_shops = []
    for row in data:
        if row['shop_name'] not in processed:
            shop = {
                'name': row['shop_name'],
                'description': row['shop_description'],
                'site_link': row['shop_link'],
                'counrty_id': get_counrty_by_id(countries, row['shop_country'])
            } 
            unique_shops.append(shop)
            processed.append(shop['name']) 
    shop_ids = db.session.scalars(
        insert(Shop).returning(Shop.id, sort_by_parameter_order=True), unique_shops
    )
    for shop_id, shop in zip(shop_ids, unique_shops):
        shop["id"] = shop_id
    return unique_shops

def get_shop_by_id(shops, shop_name):
    for shop in shops:
        if shop['name'] == shop_name:
            return shop['id']  

def save_goods(data, category_id, shops):
    processed = []
    unique_goods = []
    for row in data:
        if row['link'] not in processed:
            good = {
                'units': row.get('units'),
                'description': row.get('description'),
                'image': row.get('image'),
                'link': row.get('link'),
                'name': row['name'],
                'rating': row.get('rating'),
                'category_id': category_id,
                'shop_id': get_shop_by_id(shops, row['shop_name'])
            } 
            unique_goods.append(good)
            processed.append(good['link'])
    good_ids = db.session.scalars(
        insert(Good).returning(Good.id, sort_by_parameter_order=True), unique_goods
    )
    db.session.commit()
    for good_id, good in zip(good_ids, unique_goods):
        good["id"] = good_id
    return unique_goods

def get_currency_by_id(currencies, currency_name):
    for currency in currencies:
        if currency['name'] == currency_name:
            return currency['id']

def get_good_by_id(goods, good_link):
    for good in goods:
        if good['link'] == good_link:
            return good['id']

def save_prices(data, currencies, goods):
    prices = []
    for row in data:
        price = {
            'value': row['price'],
            'value_discount': row.get('price_discount', 0),
            'date': row['price_date'],
            'currency_id': get_currency_by_id(currencies, row['currency_name']),
            'good_id': get_good_by_id(goods, row['link'])
        } 
        prices.append(price)
    db.session.execute(insert(Price), prices)
    db.session.commit()

def save_category_items(category_name, category_items):
    app = create_app()
    with app.app_context():
        category = save_category(category_name)
        currencies = save_currencies(category_items)
        countries = save_countries(category_items)
        shops = save_shops(category_items, countries)
        goods = save_goods(category_items, category['id'], shops)
        save_prices(category_items, currencies, goods)

def execute_parser(categories, url, payload):
    for category in categories:
        category_items = get_goods_by_category(category, url, payload)
        if category_items:
            save_category_items(category, category_items)

if __name__ == '__main__':
    execute_parser(settings.CATEGORIES, settings.API_URL, settings.PAYLOAD)
