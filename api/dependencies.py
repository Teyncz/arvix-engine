from database.connection import SessionLocal, FrontSessionLocal
from database.models import RequestsUsage
from fastapi.security import APIKeyHeader, APIKeyQuery
from fastapi import Security, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Generator

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

def check_api_key( api_key_header_val: str = Security(api_key_header), api_key_query_val: str = Security(api_key_query)) -> bool:

    api_key = api_key_header_val or api_key_query_val

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    if api_key_header_val:
        if api_key.startswith("Bearer "):
            api_key = api_key.split(" ")[1]
        else:
            raise HTTPException(status_code=401, detail="Authorization header format is incorrect")

    db = FrontSessionLocal()

    try:
        result = db.execute(text("SELECT id FROM api_key WHERE key = :api_key"), {"api_key": api_key})
        user = result.fetchone()
        if user:
            return True
        else:
            raise HTTPException(status_code=401, detail="Invalid API key")
    finally:
        db.close()

def get_client_by_api_key(api_key: str):
    db = FrontSessionLocal()
    try:
        result = db.execute(text("SELECT user_id FROM api_key WHERE key = :api_key"), {"api_key": api_key})
        user = result.mappings().fetchone()
        if user:
            return user['user_id']
        else:
            return None
    finally:
        db.close()


def get_credits_amount(user_id: int):
    db = SessionLocal()
    query = (db.query(RequestsUsage).filter(RequestsUsage.user_id == user_id))
    amount = query.first()
    db.close()
    if amount:

        amount = amount.requests_number
        db_front = FrontSessionLocal()

        try:
            r = db_front.execute(text("SELECT plan.monthly_limit FROM plan INNER JOIN users ON users.plan = plan.id WHERE users.id = :user_id"), {"user_id": user_id})
            plan = r.mappings().fetchone()
            if plan:
                monthly_limit = plan['monthly_limit']

                credit_amount = monthly_limit - amount

                return credit_amount
            else:
                return None

        finally:
            db_front.close()
    else:
        return None

def get_user_limit_per_user(user_id: int):
    db_front = FrontSessionLocal()

    try:
        r = db_front.execute(text(
            "SELECT plan.minute_limit FROM plan INNER JOIN users ON users.plan = plan.id WHERE users.id = :user_id"),
                             {"user_id": user_id})
        plan = r.mappings().fetchone()
        if plan:
            minute_limit = plan['minute_limit']

            return minute_limit
        else:
            return None

    finally:
        db_front.close()