from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os
from datetime import datetime
import time
import threading
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
databaseDir = os.path.join(basedir, 'database/bitcoin_prices_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + databaseDir
db = SQLAlchemy(app)


class BitcoinPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float)


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


app_dash = dash.Dash(
    __name__,
    server=app#,
    # routes_pathname_prefix='/dash/'
)

app_dash.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.H1("Bitcoin Price Dashboard"),
    dcc.Graph(id='price-chart'),
])


@app_dash.callback(
    Output('price-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_display(n_intervals):
    prices = BitcoinPrice.query.all()
    date_list = [price.date for price in prices]
    price_list = [price.price for price in prices]

    figure = {
        'data': [
            {'x': date_list, 'y': price_list, 'type': 'line', 'name': 'Bitcoin Price'}
        ],
        'layout': {
            'title': 'Bitcoin Price'
        }
    }

    return figure


def fetch_and_update():
    with app.app_context():
        while True:
            update_price_database()
            time.sleep(60)  # Wait for 60 seconds


if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(databaseDir):
            print("Creating new database")
            db.create_all()

    # Start a new thread to fetch and update the price every minute
    update_thread = threading.Thread(target=fetch_and_update)
    update_thread.start()

    app.run(debug=True)