from fastapi import APIRouter, HTTPException
from utils.ticker import get_all_crypto, get_ticker_data
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse, TickerOverviewResponse, TickerAggregateSchema
router = APIRouter()

@router.get("/overview", response_model=TickerOverviewResponse)
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
def get_ticker_infos(ticker_code: str):
    data = get_ticker_data(ticker_code, 'CRYPTO')
    # data is a dict with keys status, message, ticker_data. Ensure ticker_data exists
    if not data or not data.get('ticker_data'):
        raise HTTPException(status_code=404, detail="Invalid ticker")
    return {
        "data": data['ticker_data'],
        "status": data['status']
    }

@router.get("/ticker/{ticker_code}/aggregate/{timeframe}/{from_date}/{to_date}", response_model=TickerAggregateResponse[TickerAggregateSchema])
def read_ticker_in_range(ticker_code: str,timeframe: str, from_date: str, to_date: str, limit: int = None, sort: str = 'asc'):
    data = get_historical_rates(ticker_code,timeframe, from_date, to_date, limit, sort, type='CRYPTO')
    if data['status'] != 'success':
        match data['error']:
            case 'INVALID TIMEFRAME':
                raise HTTPException(status_code=422, detail="Invalid timeframe")
            case 'TICKER NOT FOUND':
                raise HTTPException(status_code=404, detail="Invalid ticker")
            case 'INVALID LIMIT':
                raise HTTPException(status_code=400, detail="Invalid limit value")
            case _:
                raise HTTPException(status_code=500, detail="Error")

    return {
        "status": data['status'],
        "count": len(data['data']),
        "datetime_start" : from_date,
        "datetime_end": to_date,
        "timeframe": timeframe,
        "data": data['data'],
    }