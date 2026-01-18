from fastapi import APIRouter, HTTPException

from services.currency_service import convert_currency
from utils.ticker import get_all_crypto, get_ticker_data
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse, TickerOverviewResponse, TickerAggregateSchema, TickerSimpleAggregateSchema, CurrencyConversionResponse
from core.exceptions import TickerNotFoundException
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

@router.get("/convert", response_model=CurrencyConversionResponse)
def convert_currency_route( amount: float, base_currency: str, target_currency: str):
    conversion_result = convert_currency(base_currency, target_currency, amount)
    if not conversion_result:
        raise HTTPException(status_code=404, detail="Conversion failed")
    return {
        "status": "success",
        "data": conversion_result
    }

@router.get("/ticker/{ticker_code}", response_model=TickerDataResponse)
def get_ticker_infos(ticker_code: str):
    data = get_ticker_data(ticker_code, 'CURRENCY')

    if not data or not data.get('ticker_data'):
        raise TickerNotFoundException(ticker_code=ticker_code)

    return {
        "data": data['ticker_data'],
        "status": data['status']
    }

@router.get("/ticker/{ticker_code}/aggregate/{timeframe}/{from_date}/{to_date}", response_model=TickerAggregateResponse[TickerSimpleAggregateSchema])
def read_ticker_in_range(ticker_code: str,timeframe: str, from_date: str, to_date: str, limit: int = None, sort: str = 'asc'):
    data = get_historical_rates(ticker_code,timeframe, from_date, to_date, limit, sort, type='CURRENCY')

    return {
        "status": data['status'],
        "count": len(data['data']),
        "datetime_start" : from_date,
        "datetime_end": to_date,
        "timeframe": timeframe,
        "data": data['data'],
    }