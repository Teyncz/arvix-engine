from database.crud import insert_bulk_ticker_rate
from utils.time_utils import build_time_ranges, get_last_date_by_type
from utils.ticker import get_ticker_list_by_type
import aiohttp
import asyncio
from datetime import datetime, timezone
import random

request_count = 0

async def fetch_with_sem(sem, session, url, querystring, ticker_id, provider_code, last_entry):
    global request_count
    async with sem:
        request_count += 1

        if request_count % 20 == 0:
            print(f"--- Pause de sécurité (20 requêtes) pour l'IP Stooq... ---")
            await asyncio.sleep(5)

        await asyncio.sleep(random.uniform(1.5, 1.9))

        return await fetch_candles(session, url, querystring, ticker_id, provider_code, last_entry)

async def fetch_candles(session, url, querystring, ticker_id, provider_code, last_entry):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

    try:
        async with session.get(url, headers=headers, params=querystring) as response:

            if last_entry is None:
                last_entry = 915148800000

            if response.status == 200:
                response.raise_for_status()

                data = await response.text()
                data = [line.split(',') for line in data.split('\n')[1:] if line]

                filtered_data = []

                for row in data:
                    current_dt = datetime.strptime(row[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    current_timestamp_ms = int(current_dt.timestamp() * 1000)

                    if current_timestamp_ms > last_entry:
                        date_time = current_timestamp_ms
                        open_price = row[1]
                        close_price = row[4]
                        high_price = row[2]
                        low_price = row[3]

                        filtered_data.append((ticker_id, date_time, open_price, close_price, high_price, low_price))

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

async def run_async_acquisition(index_list, intervals, timeframe):
    tasks = []

    sem = asyncio.Semaphore(1)

    async with aiohttp.ClientSession() as session:

        last_entry = get_last_date_by_type('INDEX', timeframe)

        if not last_entry:
            last_entry = {}

        for index in index_list:

            url = f'https://stooq.com/q/d/l/?s={index["provider_code"].lower()}&i={intervals[timeframe]}'

            querystring = {}

            tasks.append(
                fetch_with_sem(
                    sem, session, url, querystring,
                    index['id'], index['provider_code'], last_entry[index['id']]
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

    print("Data insertion skipped (commented out).")

    print(f"{len(final_data_for_db)} lines were inserted.")

def fetch_index_data(timeframe):
    index_list = get_ticker_list_by_type("INDEX")

    intervals = {"day": 'd', "month": 'm', "week": 'w'}

    last_entry = get_last_date_by_type('INDEX', timeframe)

    asyncio.run(run_async_acquisition(index_list, intervals, timeframe))

