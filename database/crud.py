import calendar
from sqlalchemy import asc, desc
from datetime import datetime
from database.models import Symbol, TickerRateMinute, TickerRateDay
from psycopg2.extras import execute_values
from database.connection import engine, SessionLocal
from utils.ticker import get_ticker_id


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

def get_historical_rates(ticker_code: str, start_date: str, end_date: str, limit: int, sort: str):

    order = desc if sort == "desc" else asc

    start_date = calendar.timegm((datetime.strptime(start_date, '%Y-%m-%d')).utctimetuple()) * 1000
    end_date = calendar.timegm((datetime.strptime(end_date, '%Y-%m-%d')).utctimetuple()) * 1000

    ticker_id = get_ticker_id(ticker_code)

    if not ticker_id:
        return {'status': False, 'message': 'Ticker is not found'}

    db = SessionLocal()
    query = (db.query(TickerRateDay)
             .filter(TickerRateDay.ticker_id == ticker_id,TickerRateDay.datetime >= start_date,TickerRateDay.datetime <= end_date)
             .order_by(order(TickerRateDay.datetime)).limit(limit))
    db.close()

    return {
        "status": "success",
        "data": query.all()
    }
