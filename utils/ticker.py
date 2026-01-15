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

def get_ticker_list_by_type(ticker_type: str) -> Any:
    db = SessionLocal()

    ticker_list = db.query(Symbol).filter(Symbol.type == ticker_type).all()
    result = []
    for s in ticker_list:
        result.append({
            "id": s.id,
            "ticker": s.code,
            "provider_code": s.provider_code,
            "name": s.name
        })
    db.close()

    return result

def get_ticker(ticker_code):
    db = SessionLocal()

    ticker  = db.query(Symbol).filter(Symbol.code == ticker_code).first()

    db.close()

    if ticker:
        return {
            "id": ticker.id,
            "ticker": ticker.code,
            "provider_code": ticker.provider_code,
            "name": ticker.name,
            "type": ticker.type
        }
    return None


def get_ticker_data(ticker_code, type) :

    status = "success"
    message = False

    db = SessionLocal()
    ticker_data = db.query(Symbol).filter(Symbol.code == ticker_code, Symbol.type == type).first()
    db.close()

    if not ticker_data :
        status = "NotFound"
        message = "Ticker not found."
        return {
            "status": status,
            "message": message,
            "ticker_data": None
        }

    return {
        "status": status,
        "message": message,
        "ticker_data": {
            "ticker": ticker_data.code,
            "name": ticker_data.name,
        }
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
