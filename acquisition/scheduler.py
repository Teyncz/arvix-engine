import schedule
import time
from datetime import timezone, datetime
from crypto_scraper import initialize_crypto_data

def get_crypto_hourly():
    print('Starting hourly crypto data acquisition...')
    initialize_crypto_data('hour')

def get_crypto_daily():
    print('Starting daily crypto data acquisition...')
    initialize_crypto_data('day')

def get_crypto_weekly():
    print('Starting weekly crypto data acquisition...')
    initialize_crypto_data('week')

def get_crypto_monthly():
    now_utc = datetime.now(timezone.utc)
    if now_utc.day == 1:
        print('Starting monthly crypto data acquisition...')
        initialize_crypto_data('month')

schedule.every().hour.at(":10").do(get_crypto_hourly)
schedule.every().day.at("00:10").do(get_crypto_daily)
schedule.every().day.at("00:20").do(get_crypto_monthly)

while True:
    schedule.run_pending()
    time.sleep(1)