# Third party imports
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import norm, t

from components.option_pricing.black_scholes import BlackScholesModel, OptionType


def log_returns(price_db):
    df = price_db.copy()
    df["LogReturns"] = np.log(df["Close"]).diff()
    return df


def log_return_plot(price_db):
    price_db = log_returns(price_db)
    fig = px.line(price_db, x='Date', y='LogReturns', title='BTC Log-Returns')
    fig.update_traces(line=dict(color="red"))
    return fig


def instaneous_volatility_plot(price_db):
    price_db = log_returns(price_db)
    price_db["Volatility"] = price_db["LogReturns"].abs() * np.sqrt(365)
    fig = px.line(price_db, x='Date', y='Volatility', title='Instantaneous Volatility')
    fig.update_traces(line=dict(color="black"))
    return fig


def log_price_plot(price_db):
    df = price_db.copy()
    df["Close"] = np.log(df["Close"])
    fig = px.line(df, x='Date', y=['Close'], title='BTC Price - Log scale')
    fig.update_yaxes(title_text="Log(Price)")
    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=.98, xanchor="left", x=0.02, title=None))

    # Fit a normal distribution on the log returns
    log_returns = df['Close'].diff().dropna()
    mu, sigma = np.mean(log_returns), np.std(log_returns)

    # Expected value and variance of the geometric brownian motion
    S0 = df['Close'].iloc[0]  # The first closing price
    N = df.index.size  # The number of time steps
    t = np.arange(0, N)  # The time grid

    E_S_t = S0 + (mu * t)
    Var_S_t = (sigma ** 2 * t)

    # plots
    fig.add_scatter(x=df['Date'].iloc[-N - 1:], y=E_S_t, mode='lines', name='Expected value')
    fig.add_scatter(x=df['Date'].iloc[-N - 1:], y=E_S_t + np.sqrt(Var_S_t), mode='lines', name='Upper std bound',
                    fill=None)
    fig.add_scatter(x=df['Date'].iloc[-N - 1:], y=E_S_t - np.sqrt(Var_S_t), mode='lines', name='Lower std bound',
                    fill='tonexty', fillcolor='rgba(255,165,0,0.1)')
    return fig


def price_plot(price_db):
    fig = px.line(price_db, x='Date', y=['Close'], title='BTC Price')
    fig.update_yaxes(title_text="Price [USD]")
    fig.update_layout(showlegend=False)
    return fig


def lognormal_evolution_plot(price_db):
    df = price_db.copy()
    df["Close"] = np.log(df["Close"])
    log_returns = df['Close'].diff().dropna()
    mu, sigma = np.mean(log_returns), np.std(log_returns)
    S0 = price_db["Close"][0]
    t = np.array([50, 100, 200, 500])
    S = np.linspace(1e-3, 5000, 1000)

    def lognormal(S_, S0, mu, sigma, t):
        S = S_[:, np.newaxis]
        return (1 / (S * sigma * np.sqrt(2 * np.pi * t))) * np.exp(- np.power((np.log(S/S0) - (mu * t)), 2) / (2 * np.power(sigma, 2) * t))

    pdf = pd.DataFrame(lognormal(S, S0, mu, sigma, t), columns=t, index=S)
    fig = px.line(pdf, title='GBM pdf time evolution')
    fig.update_layout(xaxis_title="Price", yaxis_title="pdf")
    fig.add_vline(x=S0, name="0", line_dash="dot", showlegend=True, legendrank=1)
    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=.98, xanchor="right", x=0.98, title=f'{chr(916)}t [days]'))
    return fig


def rolling_volatility_plot(price_db, window=30):
    price_db = log_returns(price_db)
    price_db[f"Rolling: {window} days"] = price_db["LogReturns"].rolling(window, min_periods=np.minimum(10, window)).std() * np.sqrt(365)
    price_db["Instantaneous"] = price_db["LogReturns"].abs()*np.sqrt(365)
    fig = px.line(price_db, x='Date', y=[f"Rolling: {window} days"],
                  title=f"Historical volatility")
    ymin = 0
    ymax = price_db[f"Rolling: {window} days"].max()
    fig.update_yaxes(range=[ymin, ymax * 1.1], title_text="Volatility")
    fig.update_traces(line=dict(color="black"))
    # historical volatility
    fig.add_hline(y=price_db["LogReturns"].std()*np.sqrt(365), line_dash="dash", line_color="red",
                  name="All time",  showlegend=True)
    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=.98, xanchor="right", x=0.99, title=None))
    return fig


def log_return_histogram(price_db):
    price_db = log_returns(price_db)
    fig = px.histogram(price_db, x="LogReturns", nbins=100, title="BTC Log-Returns distribution",
                       histnorm='probability density')
    fig.data[0].name = "Empirical distribution"

    # Scipy fit
    mu, std = norm.fit(price_db.LogReturns.dropna())
    x = np.linspace(price_db.LogReturns.min(), price_db.LogReturns.max(), 100)
    p = norm.pdf(x, mu, std)

    # Student's t fit
    dof, mu_t, std_t = t.fit(price_db.LogReturns.dropna())
    p_t = t.pdf(x, dof, mu_t, std_t)

    fig.add_scatter(x=x, y=p_t, mode='lines', name="Student's t fit", line=dict(color='green', width=2))
    fig.add_scatter(x=x, y=p, mode='lines', name="Normal fit (GBM)", line=dict(color='red', width=2))
    fig.update_layout(legend=dict(orientation="v", yanchor="bottom", y=.85, xanchor="left", x=0.01))
    return fig


def log_log_return_histogram(price_db):
    fig = log_return_histogram(price_db)
    fig.update_yaxes(type="log", range=[-2, 1.6])
    return fig


def call_spot_curve(S, X, T, r, v):
    spot_prices = np.linspace(0, 2*X, 1000)
    call_prices = BlackScholesModel(spot_prices, X, T, r, v).option_price(OptionType.CALL_OPTION)
    df = pd.DataFrame(index=spot_prices)
    df.index.name = "Spot price"
    df["C(S,X,T,r,v)"] = call_prices
    df["Payoff"] = np.maximum(0, spot_prices - X)

    fig = px.line(df, x=df.index, y=df.columns, title='Call option')
    fig.update_yaxes(title_text="Option price")
    fig.add_vline(x=X, name="Strike price", line_color="green", line_dash="dot", showlegend=True)
    fig.add_vline(x=S, name="Spot price", line_color="orange", line_dash="dash", showlegend=True)
    return fig


def delta_hedging_curve(S, X, T, r, v):
    spot_prices = np.linspace(0, 2*X, 1000)
    delta_hedges = BlackScholesModel(spot_prices, X, T, r, v).delta_hedging(OptionType.CALL_OPTION)
    df = pd.DataFrame(index=spot_prices)
    df[f"{chr(916)}(S,X,T,r,v)"] = delta_hedges
    fig = px.line(df, x=df.index, y=df.columns, title='Delta hedging')
    fig.update_yaxes(title_text="Underlying held fraction")
    fig.update_xaxes(title_text="Underlying (spot) price")
    fig.add_vline(x=X, name="Strike price", line_color="green", line_dash="dot", showlegend=True)
    fig.add_vline(x=S, name="Spot price", line_color="orange", line_dash="dash", showlegend=True)
    return fig


if __name__ == "__main__":
    data = pd.read_csv("../database/BTC-USD.csv")
    fig = log_return_tails_power_law(data)
    fig.show()