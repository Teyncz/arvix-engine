import calendar
from sqlalchemy import asc, desc
from datetime import datetime
from database.models import Symbol, TickerRateMinute, TickerRateDay, TickerRateHour
from psycopg2.extras import execute_values
from database.connection import engine, SessionLocal
from utils.ticker import get_ticker_id

MODEL_MAPPING = {
    'day': TickerRateDay,
    'minute': TickerRateMinute,
    'hour': TickerRateHour,
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
    'year': 'year',
    'Y': 'year'
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


def get_historical_rates(ticker_code: str, timeframe: str, start_date: str, end_date: str, limit: Optional[int], sort: str):
    order = desc if sort == "desc" else asc

    # normalize timeframe aliases
    tf_key = TIMEFRAME_ALIASES.get(timeframe.lower(), None)
    if tf_key is None:
        return {
            "status": "error",
            "error": "INVALID TIMEFRAME"
        }

    # convert dates (YYYY-MM-DD) to milliseconds timestamps
    start_date = calendar.timegm((datetime.strptime(start_date, '%Y-%m-%d')).utctimetuple()) * 1000
    end_date = calendar.timegm((datetime.strptime(end_date, '%Y-%m-%d')).utctimetuple()) * 1000

    ticker_id = get_ticker_id(ticker_code)

    if not ticker_id:
        return {
            'status': 'error',
            'error': 'TICKER NOT FOUND'
        }

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
    try:
        query = (db.query(model_class)
                 .filter(model_class.ticker_id == ticker_id, model_class.datetime >= start_date,
                         model_class.datetime <= end_date)
                 .order_by(order(model_class.datetime)).limit(limit))

        rows = query.all()

    finally:
        db.close()

    # Map SQLAlchemy model instances to plain dicts matching the response schema aliases
    data = []
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

    return {
        "status": "success",
        "data": data
    }
