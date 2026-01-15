from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, BigInteger, Boolean, Enum as SQLAlchemyEnum
from enum import Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime, timezone
from sqlalchemy import TIMESTAMP

class Base(DeclarativeBase):
    pass

class Symbol(Base):
    __tablename__ = 'symbol'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True, nullable=False)
    provider_code = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)

    ticker_id_minute = relationship("TickerRateMinute", back_populates="symbol", foreign_keys="TickerRateMinute.ticker_id")
    ticker_id_day = relationship("TickerRateDay", back_populates="symbol", foreign_keys="TickerRateDay.ticker_id")
    ticker_id_hour = relationship("TickerRateHour", back_populates="symbol", foreign_keys="TickerRateHour.ticker_id")
    ticker_id_week = relationship("TickerRateWeek", back_populates="symbol", foreign_keys="TickerRateWeek.ticker_id")
    ticker_id_month = relationship("TickerRateMonth", back_populates="symbol", foreign_keys="TickerRateMonth.ticker_id")

class TickerRateMinute(Base):
    __tablename__ = 'ticker_rate_minute'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_minute")


class TickerRateHour(Base):
    __tablename__ = 'ticker_rate_hour'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_hour")


class TickerRateDay(Base):
    __tablename__ = 'ticker_rate_day'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_day")

class TickerRateWeek(Base):
    __tablename__ = 'ticker_rate_week'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_week")


class TickerRateMonth(Base):
    __tablename__ = 'ticker_rate_month'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    datetime = Column(BigInteger, index=True, nullable=False)
    price_high = Column(DECIMAL(18, 8), nullable=True)
    price_low = Column(DECIMAL(18, 8), nullable=True)
    price_close = Column(DECIMAL(18, 8), nullable=True)
    price_open = Column(DECIMAL(18, 8), nullable=True)

    symbol = relationship("Symbol", back_populates="ticker_id_month")

class RequestsUsage(Base):
    __tablename__ = 'requests_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    requests_number = Column(BigInteger, default=0)

class ApiKey(Base):
    __tablename__ = 'api_key'

    id = Column(String(26), primary_key=True, index=True)
    key = Column(String(40), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    revokedAt = Column(DateTime, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    userId = Column(String(26), index=True, nullable=False)

class UserStatus(Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    BANNED = "BANNED"

class User(Base):
    __tablename__ = 'user'

    id = Column(String(26), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True)
    status = Column(SQLAlchemyEnum(UserStatus), default=UserStatus.UNVERIFIED, nullable=False)
    planId = Column(Integer, ForeignKey('plan.id'), nullable=False)

class Plan(Base):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    monthlyRateLimit = Column(Integer, nullable=False)
    minuteRateLimit = Column(Integer, nullable=False)
