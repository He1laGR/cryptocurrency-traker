import streamlit as st
import requests
import pandas as pd
import arrow
import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def fetch_assets():
    """_Функция собирает объекты (имя и id криптовалюты) и возвращает их_
        assets : {'Bitcoin':'bitcoin', 'BNB': 'binance-coin'}...
    """
    url = "https://api.coincap.io/v2/assets"

    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("Failed to fetch assets")
    data = response.json()["data"]
    assets = {d["name"]: d["id"] for d in data}

    return assets


def fetch_historical_prices(asset_id, start_date, end_date, interval):
    """_Функция возвращает pd DataFrame с датой и ценой_

    Args:
        asset_id (str): _строка с id криптовалюты_
        start_date (int): _начальная дата unix ms_
        end_date (unt): _конечная дата unix ms_

    Raises:
        ValueError: _Выподает если не удалось спарсить данные_

    Returns:
        _type_: _Dataframe с датой и ценой для выбранной криптовалюты_
    """
    API_KEY = os.environ.get('COINCAP_API_KEY')

    headers = {
        "Accept-Encoding" : "gzip, deflate",
        "Authorization" : "Bearer {API_KEY}"
    }

    start_date_ms = int(arrow.get(start_date).timestamp() * 1000)
    end_date_ms = int(arrow.get(end_date).timestamp() * 1000)



    url = f"https://api.coincap.io/v2/assets/{asset_id}/history?interval={interval}&start={start_date_ms}&end={end_date_ms}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError("Failed to fetch data")
    data = response.json()["data"]
    prices = [(arrow.get(d["time"]).datetime, float(d["priceUsd"])) for d in data]
    return pd.DataFrame(prices, columns=["date", "price"])


def main():
    """_Функция для отрисовки результатов_
    """
    st.title("Cryptocurrency price chart")

    assets = fetch_assets()

    asset = st.sidebar.selectbox("Select an asset", list(assets.keys()))

    asset_id = assets[asset]

    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start date")
    end_date = col2.date_input("End date")

    if start_date > end_date:
        st.error("Error: end_date should be grater then start_date")
        return
    elif start_date == end_date:
        end_date += timedelta(days=1)


    diapason = (end_date - start_date).total_seconds() // 60
    if diapason < 1440:
        interval = "m15"
    elif diapason < 4320:
        interval = "h1"
    else:
        interval = "d1"

    prices = fetch_historical_prices(asset_id, start_date, end_date, interval)

    st.subheader(f"{asset} price between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")

    st.line_chart(prices.set_index("date"))


if __name__ == ("__main__"):
    main()
