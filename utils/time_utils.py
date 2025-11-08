import datetime
from datetime import datetime, time, timedelta, timezone
from typing import Any

from dateutil.relativedelta import relativedelta
import calendar

def get_current_date():
    now = datetime.datetime.now().date()
    return now

def calculate_past_date(days_ago):
    date = get_current_date() - datetime.timedelta(days=days_ago)
    return date

def is_ticker_up_to_day(last_date, timestamp):

    last_date_obj = datetime.fromtimestamp(last_date / 1000, tz=timezone.utc)

    match timestamp:
        case 'day':
            to_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=1)
            if last_date_obj >= to_date:
                return {'status': True}
            return {'status': False, 'next_date' : int(calendar.timegm((last_date_obj + relativedelta(days=1)).utctimetuple()) * 1000), 'to_date' : int(calendar.timegm(to_date.utctimetuple()) * 1000)}
        case 'minutes':
            return True
        case _:
            return False


def build_annual_ranges(start_date):

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = datetime.fromisoformat(start_date)

    dates: list[Any] = []

    while start_date < today:
        end_date = start_date + relativedelta(years=1)
        is_last = False

        if end_date > today:
            is_last = True
            end_date = today

        value = {'start_date': int(calendar.timegm(start_date.utctimetuple()) * 1000),'end_date': int(calendar.timegm((end_date - timedelta(days=1)).utctimetuple()) * 1000)}
        dates.append(value)


        start_date = end_date

    return dates