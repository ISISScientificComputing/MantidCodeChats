from collections import OrderedDict, namedtuple
from datetime import datetime
from threading import Timer

import requests

fee_factor = 0.9974 # 0.26% fee on every trade
currencies = OrderedDict(
    [("LTCUSD", "XLTCZUSD"), ("LTCXBT", "XLTCXXBT"), ("XBTUSD", "XXBTZUSD")])
Book = namedtuple("Book", ["bid", "ask"])

API_URL = "https://api.kraken.com/0/public/Depth"


def get_first_prices(response, pair):
    """
    Returns the first ('best price') 'bids' and 'asks'
     values for a specified pair.

    :param response: the response object (dict) from the API_URL request
    :param pair: the required currency pair
    :returns: [bid price, ask price]
    """
    return [float(response["result"][currencies[pair]][x][0][0])
            for x in ["bids", "asks"]]


def unpair(pair):
    """
    Returns a Book of prices.

    :param pair: the required currency pair
    :returns: a Book (namedtuple)
    """
    try:
        req = requests.get(API_URL, params={"pair": pair, "count": 1}).json()
        bid_price, ask_price = get_first_prices(req, pair)
        return Book(bid=bid_price, ask=ask_price)
    except Exception as e:
        print(e)


def calc(ltc_usd, ltc_xbt, xbt_usd):
    """
    Prints the forward (ltc->xbt->usd->ltc)
     and reverse (ltc->usd->btc->ltc) arbitrage factors.

    :param ltc_usd: Litecoin to USD exchange rate
    :param ltc_xbt: Litecoin to Bitcoin exchange rate
    :param xbt_usd: Bitcoin to USD exchange rate
    """
    overall_fee_factor = fee_factor**3 # Fee is taken 3 times
    forward = overall_fee_factor * ltc_xbt.bid * xbt_usd.bid / ltc_usd.ask
    reverse = overall_fee_factor * ltc_usd.bid / ltc_xbt.ask / xbt_usd.ask
    print("({}) [forward]: {:.5f}\t[reverse]: {:.5f}".format(
        datetime.now().strftime("%H:%M:%S"), forward, reverse))


def work():
    """
    Runs every 5 seconds; calls calc(...) on each currency pair.
    """
    Timer(5, work).start()
    try:
        ltc_usd, ltc_xbt, xbt_usd = [
            unpair(currency) for currency in currencies]
        calc(ltc_usd, ltc_xbt, xbt_usd)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    work()
