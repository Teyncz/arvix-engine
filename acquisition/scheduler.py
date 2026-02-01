import schedule
import time
import logging
from datetime import timezone, datetime
from crypto_scraper import initialize_crypto_data
from index_scraper import fetch_index_data
from ecb_scraper import fetch_ecb_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_run(job_func, *args):
    """Avoid scheduler crash on error."""
    try:
        job_func(*args)
    except Exception as e:
        logging.error(f"Error during execution of {job_func.__name__}: {e}")

def daily_task():
    logging.info('Starting daily data acquisition...')
    safe_run(initialize_crypto_data, 'day')
    safe_run(fetch_index_data, 'day')
    safe_run(fetch_ecb_data, 'day')

def weekly_task():
    logging.info('Starting weekly index data acquisition...')
    safe_run(fetch_index_data, 'week')

def monthly_task():
    logging.info('Starting monthly data acquisition...')
    now_utc = datetime.now(timezone.utc)
    if now_utc.day == 1:
        safe_run(initialize_crypto_data, 'month')
        safe_run(fetch_index_data, 'month')
        safe_run(fetch_ecb_data, 'month')

def get_crypto_hourly():
    logging.info('Starting hourly crypto data acquisition...')
    safe_run(initialize_crypto_data, 'hour')

#schedule.every().hour.at(":10").do(get_crypto_hourly)
schedule.every().day.at("00:10").do(daily_task)
schedule.every().sunday.at("00:15").do(weekly_task)
schedule.every().day.at("00:20").do(monthly_task)

logging.info("Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(10)