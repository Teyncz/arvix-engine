from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

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

class TickerAggregateResponse(BaseModel):
    status: str
    count: int
    datetime_start: str
    datetime_end: str
    timeframe: str
    data: List[TickerAggregateSchema]

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