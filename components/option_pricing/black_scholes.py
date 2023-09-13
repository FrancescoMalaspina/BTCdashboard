# Third party imports
import numpy as np
from scipy.stats import norm

# Local package imports
from components.option_pricing.base import OptionPriceModel, OptionType


class BlackScholesModel(OptionPriceModel):
    """
    Class implementing calculation for European option price using Black-Scholes Formula.

    Call/Put option price is calculated with following assumptions:
    - European option can be exercised only on maturity date.
    - Absence of dividents during option's lifetime.
    - Absence of credit risk: only market risk is present.
    - The risk-free rate and volatility are constant.
    - Absence of arbitrage.
    - Efficient Market Hypothesis - market movements follow a Geometric Brownian Motion:
       - Lognormal distribution of underlying returns.
    """

    def __init__(self, spot_price: float, strike_price: float, days_to_maturity: int = 100,
                 risk_free_rate: float = 0.001, volatility: float = 0.5):
        """
        Initializes variables used in Black-Scholes formula .

        :param spot_price: current underlying spot price
        :param strike_price: strike price at maturity for option contract
        :param days_to_maturity: time periods (days) to maturity/exercise date
        :param risk_free_rate: annual returns on risk-free assets (assumed constant until maturity)
        :param volatility: annual volatility of the underlying asset (assumed constant until maturity)
        """
        self.S = spot_price
        self.X = strike_price
        self.T = days_to_maturity/365
        self.r = risk_free_rate
        self.sigma = volatility

    def _call_option_price(self):
        """
        Compute price for Black&Scholes Call option.
        Formula: S*N(d1) - PresentValue(X)*N(d2), where:
         - N(d1): Delta edging -> fraction of the stock to hold for risk neutralization
         - N(d2): probability of option exercise
        """
        if self.T == 0:
            return np.maximum(self.X-self.S, 0)

        d1 = (np.log(self.S / self.X) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = (np.log(self.S / self.X) + (self.r - 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

        return self.S * norm.cdf(d1, 0.0, 1.0) - self.X * np.exp(-self.r * self.T) * norm.cdf(d2, 0.0, 1.0)

    def _put_option_price(self):
        """
        Compute price for Black&Scholes Put option.
        Formula: PresentValue(X)*N(-d2) - S*N(-d1), where:
         - N(d1): Delta edging -> fraction of the stock to hold for risk neutralization
         - N(d2): probability of option exercise
        """
        if self.T == 0:
            return np.maximum(-self.X+self.S, 0)

        d1 = (np.log(self.S / self.X) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = (np.log(self.S / self.X) + (self.r - 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

        return self.X * np.exp(-self.r * self.T) * norm.cdf(-d2, 0.0, 1.0) - self.S * norm.cdf(-d1, 0.0, 1.0)

    def delta_hedging(self, option_type: OptionType = OptionType.CALL_OPTION):
        """
        Compute the delta hedging (fraction of option asset held to netralize the risk) of a given option type
        """
        if option_type is OptionType.CALL_OPTION:
            return self._delta_hedging_call()
        elif option_type == OptionType.PUT_OPTION:
            return self._delta_hedgin_put()
        else:
            return -1

    def _delta_hedging_call(self):
        """
        :return: N(d1)
        """
        if self.T == 0:
            return 1

        d1 = (np.log(self.S / self.X) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        return norm.cdf(d1, 0.0, 1.0)

    def _delta_hedging_put(self):
        """
        :return: 1-N(-d1)
        """
        if self.T == 0:
            return 1

        d1 = (np.log(self.S / self.X) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        return 1-norm.cdf(1-d1, 0.0, 1.0)


if __name__ == "__main__":
    print(BlackScholesModel(20000, 25000, 180, 0.05, 0.75).option_price(option_type=OptionType.CALL_OPTION))

    import matplotlib.pyplot as plt
    import pandas as pd
    spot_prices = np.linspace(90, 120, 100)

    # option prices
    call_prices = pd.DataFrame(index=spot_prices, columns=np.array([1, 10, 20]))
    for T in call_prices.columns:
        call_prices[T] = BlackScholesModel(spot_prices, strike_price=100, days_to_maturity=T).option_price(
            OptionType.CALL_OPTION)
    # plot to test functionality
    call_prices.plot(label=[f"maturity: T={T}" for T in call_prices.columns])
    def payoff(S, X):
        return np.maximum(0, S-X)
    plt.plot(spot_prices, payoff(spot_prices, 100), label="payoff")
    # plt.legend()
    plt.grid()
    #plt.show()

    # delta hedging
    call_hedging = pd.DataFrame(index=spot_prices, columns=np.array([1, 10, 20]))
    for T in call_hedging.columns:
        call_hedging[T] = BlackScholesModel(spot_prices, strike_price=100, days_to_maturity=T).delta_hedging(
            OptionType.CALL_OPTION)
    # plot to test functionality
    call_hedging.plot(label=[f"maturity: T={T}" for T in call_hedging.columns])
    plt.grid()
    plt.show()
