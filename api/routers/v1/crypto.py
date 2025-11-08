from typing import List
from fastapi import APIRouter, Response, HTTPException
from utils.ticker import get_all_crypto, get_ticker_data
from api.schemas import TickerDataResponse
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
