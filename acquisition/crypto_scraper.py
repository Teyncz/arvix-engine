from database.crud import insert_bulk_ticker_rate
from utils.time_utils import build_time_ranges, get_last_date_by_type
from utils.ticker import get_all_crypto
import aiohttp
import asyncio

request_count = 0

async def fetch_with_sem(sem, session, url, querystring, crypto_id, provider_code):
    global request_count
    async with sem:
        request_count += 1

        if request_count % 200 == 0:
            print(f"--- Pause de sécurité (200 requêtes) pour l'IP Binance... ---")
            await asyncio.sleep(5)

        await asyncio.sleep(0.1)

        return await fetch_klines(session, url, querystring, crypto_id, provider_code)

async def fetch_klines(session, url, querystring, crypto_id, provider_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

    try:
        async with session.get(url, headers=headers, params=querystring) as response:

            if response.status == 200:
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
            elif response.status == 429:
                print(f"ERREUR 429 : Trop de requêtes ! Stop 30s pour {provider_code}")
                await asyncio.sleep(5)
                return []

            else:
                print(f"Erreur {response.status} pour {provider_code}")
                return []

    except Exception as e:
            print(f"Erreur réseau pour {provider_code}: {e}")
            return []

async def run_async_acquisition(crypto_list, intervals, timeframe, url):
    tasks = []

    sem = asyncio.Semaphore(15)

    async with aiohttp.ClientSession() as session:

        last_entry = get_last_date_by_type('CRYPTO', timeframe)

        delta_list = {}
        for ticker_id, datetime in last_entry.items():
            delta_list[ticker_id] = build_time_ranges(datetime, timeframe)

        for crypto in crypto_list:

            ranges_for_this_crypto = delta_list.get(crypto['id'], [])

            if not ranges_for_this_crypto:
                print(f"-> {crypto['provider_code']} est déjà à jour. Passage au suivant.")
                continue

            for date_range_item in ranges_for_this_crypto:
                querystring = {
                    "symbol": crypto['provider_code'],
                    "interval": intervals[timeframe],
                    "startTime": date_range_item['start_date'],
                    "endTime": date_range_item['end_date'],
                    "limit": 720
                }

                tasks.append(
                    fetch_with_sem(
                        sem, session, url, querystring,
                        crypto['id'], crypto['provider_code']
                    )
                )

        print(f"Starting {len(tasks)} parallel queries with rate limiting...")
        all_results = await asyncio.gather(*tasks)

    final_data_for_db = []
    for data_list in all_results:
        if data_list:
            final_data_for_db.extend(data_list)

    print(f"Acquisition completed. {len(final_data_for_db)} lines ready to be inserted.")

    insert_bulk_ticker_rate(timeframe, final_data_for_db)

    print(f"{len(final_data_for_db)} lines were inserted.")


def initialize_crypto_data(timeframe):
    url = "https://api2.binance.com/api/v3/klines"

    intervals = {"day": '1d', "minute": '1m', "hour": '1h', "month": '1M', "week": '1w'}

    crypto_list = get_all_crypto()

    last_entry = get_last_date_by_type('CRYPTO', timeframe)

    delta_list = {}
    for ticker_id, datetime in last_entry.items():
        delta_list[ticker_id] = build_time_ranges(datetime, timeframe)

    asyncio.run(run_async_acquisition(crypto_list, intervals, timeframe, url))

