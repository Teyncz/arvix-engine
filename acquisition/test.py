from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
import calendar

today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

start_date = datetime.fromisoformat("2020-01-01")

dates = []

while start_date < today:
    end_date = start_date + relativedelta(years=1)
    if end_date > today:
        end_date = today - timedelta(days=1)
    value = {'start_date': int(calendar.timegm(start_date.utctimetuple()) * 1000), 'end_date': int(calendar.timegm(end_date.utctimetuple()) * 1000)}
    dates.append(value)
    start_date = end_date + timedelta(days=1)

print(dates)