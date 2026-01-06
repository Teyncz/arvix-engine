from typing import Any

from pyexpat.errors import messages

from database.connection import SessionLocal
from database.models import Symbol, TickerRateMinute, TickerRateDay
from sqlalchemy import desc

def get_all_crypto():
    db = SessionLocal()

    crypto_list = db.query(Symbol).filter(Symbol.type == "CRYPTO").all()
    result = []
    for s in crypto_list:
        result.append({
            "id": s.id,
            "ticker": s.code,
            "provider_code": s.provider_code,
            "name": s.name
        })
    db.close()

    return result

def get_ticker_id(ticker_code):
    db = SessionLocal()

    ticker  = db.query(Symbol).filter(Symbol.code == ticker_code).first()

    db.close()

    if ticker:
        return ticker.id
    return None


def get_ticker_data(ticker_code) :

    db = SessionLocal()

    status = "success"
    message = False

    ticker_data = db.query(Symbol).filter(Symbol.code == ticker_code).first()

    if not ticker_data :
        status = "NotFound"
        message = "Ticker not found."

    db.close()

    return {
        "status": status,
        "message": message,
        "ticker_data": ticker_data
    }


def get_last_row_date(ticker_id, timeframe):
    db = SessionLocal()

    models = {"minute": TickerRateMinute, "day": TickerRateDay}

    model = models[timeframe]

    if not model:
        return None

    last_date = db.query(model).filter(model.ticker_id == ticker_id).order_by(desc(model.datetime)).first()

    db.close()

    return last_date.datetime
