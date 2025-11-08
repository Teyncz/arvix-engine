from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TickerDataSchema(BaseModel):

    code: str = Field(alias="ticker")
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






