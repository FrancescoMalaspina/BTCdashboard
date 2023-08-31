from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# databaseDir = os.path.join("../", basedir, 'database/bitcoin_prices.db')
databaseDir = os.path.abspath("/Users/Franci/ProgrammingProjects/BTCdashboard/database/bitcoin_prices.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + databaseDir
db = SQLAlchemy(app)


class BitcoinPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float)


@app.route('/')
def index():
    prices = BitcoinPrice.query.all()
    return render_template('base.html', prices=prices)


def fetch_bitcoin_price():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    response = requests.get(url)
    data = json.loads(response.text)
    rate = data['bpi']['USD']['rate_float']
    return float(rate)


def update_price_database():
    price = fetch_bitcoin_price()
    now = datetime.utcnow()
    price_data = BitcoinPrice(date=now, price=price)
    db.session.add(price_data)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(databaseDir):
            print("Creating new database")
            db.create_all()
        update_price_database()
    app.run()
