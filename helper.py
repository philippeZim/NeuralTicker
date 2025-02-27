import yfinance as yf
import requests

def extract(close_data):
    price = float(close_data.iloc[-1])

    try:
        week = float(100 * (close_data.iloc[-1] - close_data.iloc[-2]) / close_data.iloc[-2])
    except:
        week = None
    try:
        month = float(100 * (close_data.iloc[-1] - close_data.iloc[-5]) / close_data.iloc[-5])
    except:
        month = None
    try:
        year = float(100 * (close_data.iloc[-1] - close_data.iloc[0]) / close_data.iloc[0])
    except:
        year = None

    result = {
        "price": price,
        "week": week,
        "month": month,
        "year": year
    }
    return result

def get_data_single(ticker):
    data = yf.Ticker(ticker)

    data_hist = data.history(period="1y", interval="1wk")

    close_data = data_hist["Close"]

    return extract(close_data)

def get_data(tickers):
    tickers_str = " ".join(tickers)
    data = yf.download(tickers_str, period="1y", interval="1wk")

    res = []

    all_close_data = data["Close"]

    for ticker in tickers:
        res.append(extract(all_close_data[ticker]))

    return res


