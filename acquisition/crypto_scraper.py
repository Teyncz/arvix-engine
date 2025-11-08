from database.crud import insert_bulk_ticker_rate
from utils.time_utils import build_annual_ranges, is_ticker_up_to_day
from utils.ticker import get_all_crypto, get_last_row_date
from requests import request
import json


def initialize_crypto_data():
    url = "https://api2.binance.com/api/v3/klines"

    payload = ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

    date_range = build_annual_ranges('2020-01-01')

    crypto_list = get_all_crypto()

    for crypto in range(len(crypto_list)):
        for date in range(len(date_range)):
            querystring = {"symbol": crypto_list[crypto].provider_code, "interval": "1d", "startTime": date_range[date]['start_date'],"endTime": date_range[date]['end_date']}

            response = request("GET", url, data=payload, headers=headers, params=querystring)
            data = json.loads(response.text)

            filtered_data = []

            for row in data:
                date_time = int(row[0])
                open_price = float(row[1])
                close_price = float(row[4])
                high_price = float(row[2])
                low_price = float(row[3])

                filtered_data.append([crypto_list[crypto].id, date_time, open_price, close_price, high_price, low_price])

            insert_bulk_ticker_rate('day', filtered_data)

def get_crypto_data(timeframe):

    url = "https://api2.binance.com/api/v3/klines"

    payload = ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

    crypto_list = get_all_crypto()

    intervals = {"minute": '1m', "day": '1d'}

    interval = intervals[timeframe]

    for crypto in range(len(crypto_list)):
        last_date = get_last_row_date(crypto_list[crypto].id, timeframe)
        is_data_current = is_ticker_up_to_day(last_date, timeframe)

        if is_data_current['status']:
            print('Data is up to date for ' + crypto_list[crypto].code + ' in ' + timeframe + ' timeframe')
        else:
            querystring = {"symbol": crypto_list[crypto].provider_code, "interval": interval, "startTime": is_data_current['next_date'], "endTime": is_data_current['to_date']}

            response = request("GET", url, data=payload, headers=headers, params=querystring)
            data = json.loads(response.text)

            filtered_data = []

            for row in data:
                date_time = int(row[0])
                open_price = float(row[1])
                close_price = float(row[4])
                high_price = float(row[2])
                low_price = float(row[3])

                filtered_data.append([crypto_list[crypto].id, date_time, open_price, close_price, high_price, low_price])

            insert_bulk_ticker_rate('day', filtered_data)

            print('Inserted ' + len(data) + ' row(s) for ' + crypto_list[crypto].code + ' in ' + timeframe + ' timeframe')

get_crypto_data('day')