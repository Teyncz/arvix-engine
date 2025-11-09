from database.connection import SessionLocal, FrontSessionLocal
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

