from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import TIMESTAMP

class Base(DeclarativeBase):
    pass

class Symbol(Base):
    __tablename__ = 'symbol'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    provider_code = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)

    ticker_id_minute = relationship("TickerRateMinute", back_populates="symbol", foreign_keys="TickerRateMinute.ticker_id")
    ticker_id_day = relationship("TickerRateDay", back_populates="symbol", foreign_keys="TickerRateDay.ticker_id")

class TickerRateMinute(Base):
    __tablename__ = 'ticker_rate_minute'

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_minute")

class TickerRateDay(Base):
    __tablename__ = 'ticker_rate_day'

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_day")


class RequestsUsage(Base):
    __tablename__ = 'requests_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    requests_number = Column(BigInteger, default=0)
