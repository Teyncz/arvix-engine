from fastapi import APIRouter, HTTPException, Query

from services.currency_service import convert_currency
from utils.ticker import get_ticker_list_by_type, get_ticker_data
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse, TickerOverviewResponse, TickerAggregateSchema, \
    TickerSimpleAggregateSchema, CurrencyConversionResponse
from core.exceptions import TickerNotFoundException, ServiceUnexpectedError

router = APIRouter()

@router.get("/overview", response_model=TickerOverviewResponse)
async def read_overview():
    data = get_ticker_list_by_type("CURRENCY")

    if not data or not data.get('data'):
        raise ServiceUnexpectedError()

    return {
        "count": len(data),
        "data": data,
        "status": "success"
    }

@router.get("/convert", response_model=CurrencyConversionResponse)
async def convert_currency_route(
        amount: float = Query(..., gt=0),
        base_currency: str = Query(..., min_length=3, max_length=3),
        target_currency: str = Query(..., min_length=3, max_length=3),
):
    conversion_result = convert_currency(base_currency, target_currency, amount)

    if not conversion_result:
        raise HTTPException(status_code=404, detail="Conversion failed")

    return {
        "status": "success",
        "data": conversion_result
    }

@router.get("/ticker/{ticker_code}", response_model=TickerDataResponse)
async def get_ticker_infos(ticker_code: str):
    data = get_ticker_data(ticker_code, 'CURRENCY')

    if not data or not data.get('ticker_data'):
        raise TickerNotFoundException(ticker_code=ticker_code)

    return {
        "data": data['ticker_data'],
        "status": data['status']
    }

@router.get("/ticker/{ticker_code}/aggregate/{timeframe}/{from_date}/{to_date}", response_model=TickerAggregateResponse[TickerSimpleAggregateSchema])
async def read_ticker_in_range(
        ticker_code: str,
        timeframe: str,
        from_date: str,
        to_date: str,
        limit: int = Query(None, le=1440),
        sort: str = Query('asc', regex="^(asc|desc)$")
):
    data = get_historical_rates(ticker_code, timeframe, from_date, to_date, limit, sort, type='CURRENCY')

    if not data or not data.get('data'):
        raise ServiceUnexpectedError()

    return {
        "status": data['status'],
        "count": len(data['data']),
        "datetime_start": from_date,
        "datetime_end": to_date,
        "timeframe": timeframe,
        "data": data['data'],
    }
