from enum import Enum
from abc import ABC, abstractmethod


class OptionType(Enum):
    CALL_OPTION = 'Call Option'
    PUT_OPTION = 'Put Option'


class OptionPriceModel(ABC):
    """Abstract class defining interface for Call and Put option pricing models."""
    def option_price(self, option_type: OptionType = OptionType.CALL_OPTION):
        """
        Compute the option price for a given option type.

        :param option_type: an OptionType enum value indicating whether the option is a call or a put
        :return: a float value representing the option price
        """
        if option_type is OptionType.CALL_OPTION:
            return self._call_option_price()
        elif option_type == OptionType.PUT_OPTION:
            return self._put_option_price()
        else:
            return -1

    @abstractmethod
    def _call_option_price(self):
        """Compute option price for call option."""
        pass

    @abstractmethod
    def _put_option_price(self):
        """Compute option price for put option."""
        pass