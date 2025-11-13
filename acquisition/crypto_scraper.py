from database.crud import insert_bulk_ticker_rate
from utils.time_utils import build_time_ranges, is_ticker_up_to_day
from utils.ticker import get_all_crypto, get_last_row_date
from requests import request
import aiohttp
import asyncio
import json


async def fetch_klines(session, url, querystring, crypto_id, provider_code):

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

    async with session.get(url, headers=headers, params=querystring) as response:
        response.raise_for_status()

        data = await response.json()

        filtered_data = []

        for row in data:
            date_time = int(row[0])
            open_price = float(row[1])
            close_price = float(row[4])
            high_price = float(row[2])
            low_price = float(row[3])

            filtered_data.append((crypto_id, date_time, open_price, close_price, high_price, low_price))

        return filtered_data

async def run_async_acquisition(crypto_list, date_range, intervals, timeframe, url):
    tasks = []

    async with aiohttp.ClientSession() as session:

        for crypto in crypto_list:
            for date_range_item in date_range:
                querystring = {
                    "symbol": crypto.provider_code,
                    "interval": intervals[timeframe],
                    "startTime": date_range_item['start_date'],
                    "endTime": date_range_item['end_date'],
                    "limit": 720
                }

                tasks.append(
                    fetch_klines(
                        session,
                        url,
                        querystring,
                        crypto.id,
                        crypto.provider_code
                    )
                )

        print(f"Starting {len(tasks)} parallel queries...")

        all_results = await asyncio.gather(*tasks)

    final_data_for_db = []
    for data_list, anomaly_list in all_results:
        final_data_for_db.extend(data_list)

    print(f"Acquisition completed. {len(final_data_for_db)} lines ready to be inserted.")

    insert_bulk_ticker_rate(timeframe, final_data_for_db)

    print(f"{len(final_data_for_db)} lines were inserted.")


def initialize_crypto_data(timeframe):

    url = "https://api2.binance.com/api/v3/klines"

    payload = ""

    start_date = {"day": '2020-01-01', "minute": '2025-05-01'}

    date_range = build_time_ranges(start_date[timeframe], timeframe)

    print(date_range)
    print(len(date_range))

    intervals = {"day": '1d', "minute": '1m'}

    crypto_list = get_all_crypto()

    asyncio.run(run_async_acquisition(crypto_list, date_range, intervals, timeframe, url))

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

initialize_crypto_data('minute')