from fastapi import APIRouter, HTTPException
from utils.ticker import get_all_crypto, get_ticker_data
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse
router = APIRouter()

@router.get("/overview", response_model=TickerDataResponse)
def read_overview():
    data = get_all_crypto()
    if not data :
        raise HTTPException(status_code=404, detail="Data not found")
    return {
        "count": len(data),
        "data": data,
        "status": "success"
    }

@router.get("/ticker/{ticker_code}", response_model=TickerDataResponse)
def read_overview(ticker_code: str):
    data = get_ticker_data(ticker_code)
    if not data :
        raise HTTPException(status_code=404, detail="Invalid ticker")
    return {
        "data": data['ticker_data'],
        "status": data['status']
    }

@router.get("/ticker/{ticker_code}/aggregate/{from_date}/{to_date}", response_model=TickerAggregateResponse)
def read_overview(ticker_code: str, from_date: str, to_date: str, limit: int = None, sort: str = 'asc'):
    data = get_historical_rates(ticker_code, from_date, to_date, limit, sort)
    if not data :
        raise HTTPException(status_code=404, detail="Invalid ticker")
    return {
        "status": data['status'],
        "count": len(data['data']),
        "datetime_start" : from_date,
        "datetime_end": to_date,
        "data": data['data'],
    }