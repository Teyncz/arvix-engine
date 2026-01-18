from pydantic import BaseModel, Field
from datetime import datetime
from typing import TypeVar, Generic, List

T = TypeVar("T")

# --------- Currency Schema --------- #

class CurrencyConversionSchema(BaseModel):
    base_currency: str = Field(alias="base_currency")
    target_currency: str = Field(alias="target_currency")
    input_amount: float = Field(alias="input_amount")
    converted_amount: float = Field(alias="converted_amount")
    exchange_rate: float = Field(alias="exchange_rate")
    last_update: int = Field(alias="last_update")

class CurrencyConversionResponse(BaseModel):
    status: str
    data: CurrencyConversionSchema

# --------- Ticker Schema --------- #

class TickerDataSchema(BaseModel):

    ticker: str
    name: str

    class Config:
        from_attributes = True
        populate_by_name = True

class TickerOverviewResponse(BaseModel):
    status: str
    count: int
    data: List[TickerDataSchema]

class TickerDataResponse(BaseModel):
    status: str
    data: TickerDataSchema

class TickerAggregateSchema(BaseModel):

    datetime: int
    price_open: float = Field(alias="open")
    price_close: float = Field(alias="close")
    price_high: float = Field(alias="high")
    price_low: float = Field(alias="low")

    class Config:
        from_attributes = True
        populate_by_name = True

class TickerSimpleAggregateSchema(BaseModel):
    datetime: int
    price: float = Field(validation_alias="open", serialization_alias="rate")
    class Config:
        from_attributes = True
        populate_by_name = True

class TickerAggregateResponse(BaseModel, Generic[T]):
    status: str
    count: int
    datetime_start: str
    datetime_end: str
    timeframe: str
    data: List[T]

# --------- Admin Schema --------- #

class ApiKeySyncSchema(BaseModel):
    key_id: str
    key: str
    name: str
    user_id: str

class EditApiKeySyncSchema(BaseModel):
    key_id: str
    status: bool | None = None
    name: str | None = None

class UserUsage(BaseModel):
    user_id: str

class DeleteApiKeySyncSchema(BaseModel):
    key_id: str

class UserSyncSchema(BaseModel):
    user_id: str
    email: str