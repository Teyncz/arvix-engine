import datetime
from sqlalchemy import func
from datetime import datetime, time, timedelta, timezone
from database.connection import SessionLocal
from database.models import TickerRateMinute, TickerRateDay, TickerRateHour, Symbol, TickerRateMonth, TickerRateWeek
from typing import Any

from dateutil.relativedelta import relativedelta
import calendar


# Get current date
def get_current_date():
    now = datetime.datetime.now().date()
    return now

# Calculate past date by days ago
def calculate_past_date(days_ago):
    date = get_current_date() - datetime.timedelta(days=days_ago)
    return date

# Check if ticker is up to date for given timeframe
def is_ticker_up_to_day(last_date, timestamp):
    last_date_obj = datetime.fromtimestamp(last_date / 1000, tz=timezone.utc)

    match timestamp:
        case 'day':
            to_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
                days=1)
            if last_date_obj >= to_date:
                return {'status': True}
            return {'status': False,
                    'next_date': int(calendar.timegm((last_date_obj + relativedelta(days=1)).utctimetuple()) * 1000),
                    'to_date': int(calendar.timegm(to_date.utctimetuple()) * 1000)}
        case 'minutes':
            return True
        case _:
            return False


# Get last date for all tickers by type ( ex: all crypto last date for 'day' timeframe )
def get_last_date_by_type(ticker_type, timeframe):
    db = SessionLocal()

    models = {"minute": TickerRateMinute, "day": TickerRateDay, "hour": TickerRateHour, "month": TickerRateMonth, "week": TickerRateWeek}

    model = models.get(timeframe)

    if not model:
        db.close()
        return None

    results = (
        db.query(
            Symbol.id,
            func.max(model.datetime)
        )
        .join(model, Symbol.id == model.ticker_id, isouter=True)
        .filter(Symbol.type == ticker_type)
        .group_by(Symbol.id)
        .order_by(Symbol.id)
        .all()
    )

    last_dates = {id: last_date for id, last_date in results}

    return last_dates


def build_raw_time_ranges(timeframe, ticker_list):
    results = {}

    for ticker_id, datetime in ticker_list.items():
        results[ticker_id] = build_time_ranges(datetime, timeframe)

    print(results)

# Get
def build_time_ranges(start_date, timeframe):
    start_dates_default = {"day": '2020-01-01', "minute": '2025-05-01', "hour": '2023-01-01', "month": '2020-01-01', "week": '2020-01-01'}

    if start_date is None:
        start_date = start_dates_default[timeframe]

    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)

    if isinstance(start_date, datetime):
        pass

    elif isinstance(start_date, (int, float)):
        if start_date > 1e11:
            start_date = start_date / 1000
        start_date = datetime.fromtimestamp(start_date)

    dates: list[Any] = []

    match timeframe:
        case 'week':
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            while start_date < today:
                end_date = start_date + relativedelta(years=10)
                is_last = False

                if end_date > today:
                    is_last = True
                    end_date = today

                value = {'start_date': int(calendar.timegm(start_date.utctimetuple()) * 1000),
                         'end_date': int(calendar.timegm((end_date - timedelta(days=1)).utctimetuple()) * 1000)}
                dates.append(value)
                start_date = end_date

            return dates

        case 'month':
            today = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            while start_date < today:
                end_date = start_date + relativedelta(years=10)
                is_last = False

                if end_date > today:
                    is_last = True
                    end_date = today

                value = {'start_date': int(calendar.timegm(start_date.utctimetuple()) * 1000),
                         'end_date': int(calendar.timegm((end_date - timedelta(days=1)).utctimetuple()) * 1000)}
                dates.append(value)
                start_date = end_date

            return dates

        case 'hour':
            today = datetime.today().replace(minute=0, second=0, microsecond=0) - relativedelta(hours=2)
            while start_date < today:
                end_date = start_date + relativedelta(days=12)
                is_last = False

                if end_date >= today:
                    is_last = True
                    end_date = datetime.today().replace(minute=0, second=0, microsecond=0) - relativedelta(hours=2)

                value = {'start_date': int(calendar.timegm((start_date + timedelta(hours=1)).utctimetuple()) * 1000),
                         'end_date': int(calendar.timegm((end_date).utctimetuple()) * 1000)}
                dates.append(value)
                start_date = end_date

            return dates

        case 'day':
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            while start_date < today:
                end_date = start_date + relativedelta(years=1)
                is_last = False

                if end_date > today:
                    is_last = True
                    end_date = today

                value = {'start_date': int(calendar.timegm(start_date.utctimetuple()) * 1000),
                         'end_date': int(calendar.timegm((end_date - timedelta(days=1)).utctimetuple()) * 1000)}
                dates.append(value)
                start_date = end_date

            return dates
        case 'minute':
            today = datetime.today().replace(second=0, microsecond=0) - relativedelta(minutes=1)
            while start_date < today:
                end_date = start_date + relativedelta(hours=12)
                is_last = False

                if end_date >= today:
                    is_last = True
                    end_date = datetime.today().replace(second=0, microsecond=0) - relativedelta(minutes=1)

                value = {'start_date': int(calendar.timegm((start_date + timedelta(minutes=1)).utctimetuple()) * 1000),
                         'end_date': int(calendar.timegm((end_date).utctimetuple()) * 1000)}
                dates.append(value)

                start_date = end_date

            return dates
        case _:
            return False
