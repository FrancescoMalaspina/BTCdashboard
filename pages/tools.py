# Third party imports
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import norm

from .option_pricing.black_scholes import BlackScholesModel, OptionType


def log_returns(price_db):
    price_db["LogReturns"] = np.log(price_db["Close"]) - np.log(price_db["Close"].shift(1))
    return price_db


def log_return_chart(price_db):
    price_db = log_returns(price_db)
    fig = px.line(price_db, x='Date', y='LogReturns', title='BTC Log-Returns')
    fig.update_traces(line=dict(color="red"))
    return fig


def rolling_volatility_chart(price_db, window=30):
    price_db = log_returns(price_db)
    price_db["rollingVolatility"] = price_db["LogReturns"].rolling(window).std() * np.sqrt(365)
    fig = px.line(price_db, x='Date', y="rollingVolatility",
                  title=f"BTC rolling (annualized) volatility for the previous {window} days",
                  labels="Rolling Volatility")
    ymin = 0
    ymax = price_db["rollingVolatility"].max()
    fig.update_yaxes(range=[ymin, ymax * 1.1])
    fig.update_traces(line=dict(color="black"))
    # historical volatility
    fig.add_hline(y=price_db["LogReturns"].std()*np.sqrt(365), line_dash="dash", line_color="red", name="Historical Volatility")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=.99, xanchor="left", x=0))
    fig.update_layout(showlegend=True)
    return fig


def log_return_histogram(price_db):
    fig = px.histogram(price_db, x="LogReturns", nbins=100, title="BTC Log-Returns distribution",
                       histnorm='probability density')
    fig.data[0].name = "Empirical distribution"

    # Scipy fit
    mu, std = norm.fit(price_db.LogReturns.dropna())
    x = np.linspace(price_db.LogReturns.min(), price_db.LogReturns.max(), 100)
    p = norm.pdf(x, mu, std)

    # Add normal fit line to figure
    # name = f"Normal fit: $\\mu$={mu:.1e}, $\\sigma$={std:.1e}"
    name = "Normal fit: Theoretical GBM distribution"
    fig.add_scatter(x=x, y=p, mode='lines', name=name, line=dict(color='red', width=2))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=.85, xanchor="left", x=0.01))
    return fig


def log_log_return_histogram(price_db):
    fig = px.histogram(price_db, x="LogReturns", nbins=100, title="BTC Log-Returns distribution: Log scale",
                       histnorm='probability density')
    fig.data[0].name = "Empirical distribution"

    # Scipy fit
    mu, std = norm.fit(price_db.LogReturns.dropna())
    x = np.linspace(price_db.LogReturns.min(), price_db.LogReturns.max(), 100)
    p = norm.pdf(x, mu, std)

    # Add normal fit line to figure
    # name = f"Normal fit: $\\mu$={mu:.1e}, $\\sigma$={std:.1e}"
    name = "Normal fit: Theoretical GBM distribution"
    fig.add_scatter(x=x, y=p, mode='lines', name=name, line=dict(color='red', width=2))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=.85, xanchor="left", x=0.01))
    fig.update_yaxes(type="log", range=[-2, 1.6])
    return fig


def call_spot_curve(X, T, r, v):
    spot_prices = np.linspace(X/2, 3*X/2, 1000)
    call_prices = BlackScholesModel(spot_prices, X, T, r, v).option_price(OptionType.CALL_OPTION)

    fig = px.line(call_prices, x=spot_prices, y=call_prices, labels={"x": "Spot Price", "y": "Option Price"}, name="Option price")
    fig.add_scatter(x=spot_prices, y=np.maximum(0, spot_prices - X), mode="lines", name="Payoff")
    return fig


if __name__ == "__main__":
    data = pd.read_csv("../database/BTC-USD.csv")
    print(log_returns(data))
    fig = rolling_volatility_chart(data)
    #fig.show()
    fig = log_return_histogram(data)
    fig.show()