from datetime import datetime, date, time, timedelta
import calendar

start = "2022-01-01"
end = "2022-02-01"

start_date = calendar.timegm((datetime.strptime(start, '%Y-%m-%d')).utctimetuple()) * 1000
end_date = calendar.timegm((datetime.strptime(end, '%Y-%m-%d')).utctimetuple()) * 1000

print(start_date, end_date)