import calendar
from sqlalchemy import func, desc, asc
from datetime import datetime
from database.models import Symbol, TickerRateMinute, TickerRateDay, TickerRateHour, TickerRateMonth, TickerRateWeek
from psycopg2.extras import execute_values
from database.connection import engine, SessionLocal
from utils.ticker import get_ticker
from core.exceptions import TickerNotFoundException, InvalidTimeframeException

MODEL_MAPPING = {
    'day': TickerRateDay,
    'minute': TickerRateMinute,
    'hour': TickerRateHour,
    'month': TickerRateMonth,
    'week': TickerRateWeek,
}

# Accept common timeframe aliases (e.g. 1D -> day)
TIMEFRAME_ALIASES = {
    '1d': 'day',
    'day': 'day',
    'd': 'day',
    '1m': 'minute',
    '1h': 'hour',
    'minute': 'minute',
    'min': 'minute',
    'month': 'month',
    'M': 'month',
    '1M': 'month',
    'week': 'week',
    '1w': 'week',
    'w': 'week',
    'year': 'month',
    'y': 'month',
}


def insert_bulk_ticker_rate(timeframe, data):
    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cursor:
            sql_command = f"""
                INSERT INTO ticker_rate_{timeframe}
                (ticker_id, datetime, price_high, price_low, price_close, price_open)
                VALUES %s
            """

            execute_values(
                cursor,
                sql_command,
                data,
                page_size=5000
            )

            raw_conn.commit()
            return cursor.rowcount

    except Exception as e:
        raw_conn.rollback()
        raise Exception(f"Erreur Bulk Insert: {e}")
    finally:
        raw_conn.close()


def get_historical_rates(ticker_code: str, timeframe: str, start_date: str, end_date: str, limit: Optional[int],sort: str, type: str = 'INDEX') :
    order = desc if sort == "desc" else asc
    ticker = get_ticker(ticker_code)

    ticker_type = ticker.get('type') if ticker else None

    if ticker_type is None or ticker_type != type:
        raise TickerNotFoundException(ticker_code = ticker_code)

    # normalize timeframe aliases
    tf_key = TIMEFRAME_ALIASES.get(timeframe, None)
    if tf_key is None:
        raise InvalidTimeframeException()

    # convert dates (YYYY-MM-DD) to milliseconds timestamps
    ts_start_date = calendar.timegm((datetime.strptime(start_date, '%Y-%m-%d')).utctimetuple()) * 1000
    ts_end_date = calendar.timegm((datetime.strptime(end_date, '%Y-%m-%d')).utctimetuple()) * 1000

    ticker_id = ticker['id']

    if not ticker_id:
        raise TickerNotFoundException(ticker_code=ticker_code)

    model_class = MODEL_MAPPING.get(tf_key)

    # Default/limit protections
    # Normalize and validate limit: accept None, empty, strings containing numbers, etc.
    if limit in (None, ""):
        limit = 1440
    else:
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return {"status": "error", "error": "INVALID LIMIT"}

    if limit <= 0:
        return {"status": "error", "error": "INVALID LIMIT"}

    # hard cap to prevent huge queries
    if limit > 1440:
        limit = 1440

    if model_class is None:
        return {
            "status": "error",
            "error": "INVALID TIMEFRAME"
        }

    db = SessionLocal()

    data = []

    if timeframe not in ['year', 'y']:

        try:
            query = (db.query(model_class)
                     .filter(model_class.ticker_id == ticker_id, model_class.datetime >= ts_start_date,
                             model_class.datetime <= ts_end_date)
                     .order_by(order(model_class.datetime)).limit(limit))

            rows = query.all()

        finally:
            db.close()

        # Map SQLAlchemy model instances to plain dicts matching the response schema aliases
        for r in rows:
            try:
                item = {
                    "datetime": getattr(r, 'datetime'),
                    "open": getattr(r, 'price_open'),
                    "close": getattr(r, 'price_close'),
                    "high": getattr(r, 'price_high'),
                    "low": getattr(r, 'price_low'),
                }
                data.append(item)
            except Exception:
                # If unexpected model shape, skip the row
                continue

    elif timeframe in ['year', 'y']:

        get_time_range = list(range(int(start_date[:4]), int(end_date[:4]) + 1))

        for t in get_time_range:

            ts_start = int(datetime(t, 1, 1).timestamp()) * 1000
            ts_end = int(datetime(t, 12, 31, 23, 59, 59).timestamp()) * 1000

            try :
                query = (db.query(model_class)
                         .filter(model_class.ticker_id == ticker_id, model_class.datetime >= ts_start,
                                 model_class.datetime < ts_end)
                         .order_by(order(model_class.datetime)).limit(limit))

            finally:
                db.close()

            rows = query.all()

            if rows:
                max_high = max(getattr(r, 'price_high') for r in rows)
                min_low = min(getattr(r, 'price_low') for r in rows)

                year_data = {
                    "datetime": getattr(rows[0], 'datetime'),
                    "open": getattr(rows[0], 'price_open'),
                    "close": getattr(rows[-1], 'price_close'),
                    "high": max_high,
                    "low": min_low,
                }

                data.append(year_data)


    return {
            "status": "success",
            "data": data
        }
