from fastapi import APIRouter, HTTPException
from utils.ticker import get_all_crypto, get_ticker_data, get_ticker_list_by_type
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse, TickerOverviewResponse, TickerAggregateSchema
from core.exceptions import TickerNotFoundException, ServiceUnexpectedError

router = APIRouter()

@router.get("/overview", response_model=TickerOverviewResponse)
async def read_overview():
    data = get_ticker_list_by_type("INDEX")

    if not data:
        raise ServiceUnexpectedError()

    return {
        "count": len(data),
        "data": data,
        "status": "success"
    }

@router.get("/ticker/{ticker_code}", response_model=TickerDataResponse)
def get_ticker_infos(ticker_code: str):
    data = get_ticker_data(ticker_code, 'INDEX')

    if not data or not data.get('ticker_data'):
        raise TickerNotFoundException(ticker_code=ticker_code)

    return {
        "data": data['ticker_data'],
        "status": data['status']
    }

@router.get("/ticker/{ticker_code}/aggregate/{timeframe}/{from_date}/{to_date}", response_model=TickerAggregateResponse[TickerAggregateSchema])
def read_ticker_in_range(ticker_code: str,timeframe: str, from_date: str, to_date: str, limit: int = None, sort: str = 'asc'):
    data = get_historical_rates(ticker_code,timeframe, from_date, to_date, limit, sort, type='INDEX')

    return {
        "status": data['status'],
        "count": len(data['data']),
        "datetime_start" : from_date,
        "datetime_end": to_date,
        "timeframe": timeframe,
        "data": data['data'],
    }