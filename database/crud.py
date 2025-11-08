from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func
from .models import Symbol, TickerRateMinute
from datetime import date
from psycopg2.extras import execute_values
from .connection import engine
from utils.time_utils import get_current_date, calculate_past_date

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

def insert_bulk_rates(data_to_insert: list):

    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cursor:
            sql_command = """
                INSERT INTO currency_daily_rate
                (date, rate, base_currency_id, target_currency_id)
                VALUES %s
            """

            execute_values(
                cursor,
                sql_command,
                data_to_insert,
                page_size=5000
            )

            raw_conn.commit()
            return cursor.rowcount

    except Exception as e:
            raw_conn.rollback()
            raise Exception(f"Erreur Bulk Insert: {e}")
    finally:
        raw_conn.close()


def get_historical_rates_range (db: Session, target_code: int, days: int):

    target_date = calculate_past_date(days)

    result = db.query(CurrencyDailyRate).filter(CurrencyDailyRate.target_currency_id == target_code, CurrencyDailyRate.date >= target_date).order_by(CurrencyDailyRate.date.desc()).all()

    return result


def get_last_recorded_date(db: Session, base_id: int, target_id: int):

    latest_date_result = db.query( func.max(CurrencyDailyRate.date)).filter(CurrencyDailyRate.base_currency_id == base_id,CurrencyDailyRate.target_currency_id == target_id).scalar()

    return latest_date_result.date()