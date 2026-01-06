from database.connection import SessionLocal, FrontSessionLocal
from database.models import RequestsUsage, ApiKey, User, Plan
from fastapi.security import APIKeyHeader, APIKeyQuery
from fastapi import Security, HTTPException, status, Query, Header
from sqlalchemy import text, func
from core.config import SYNC_API_SECRET
from sqlalchemy.orm import Session
from typing import Generator, Annotated

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


def check_api_key(api_key_header_val: str = Security(api_key_header),
                  api_key_query_val: str = Security(api_key_query)) -> bool:
    api_key = api_key_header_val or api_key_query_val

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    if api_key_header_val:
        if api_key.startswith("Bearer "):
            api_key = api_key.split(" ")[1]
        else:
            raise HTTPException(status_code=401, detail="Authorization header format is incorrect")

    db: Session | None = None

    try:
        db = SessionLocal()
        key = db.query(ApiKey).filter(ApiKey.key == api_key, ApiKey.status == True).first()

        if key:
            return True
        else:
            raise HTTPException(status_code=401, detail="Invalid or Inactive API key")
    finally:
        db.close()


def get_client_by_api_key(api_key: str):
    db: Session | None = None

    try:
        db = SessionLocal()

        key = db.query(ApiKey).filter(ApiKey.key == api_key, ApiKey.status == True).first()

        return key.userId if key else None
    except Exception as ex:
        raise HTTPException(status_code=401, detail="Invalid API key")

    finally:
        if db:
            db.close()


def get_credits_amount(user_id: str, with_limit: bool = False):
    db = SessionLocal()

    try:
        amount_used_query = db.query(func.sum(RequestsUsage.requests_number)).filter(
            RequestsUsage.user_id == user_id).scalar()

        amount_used = amount_used_query if amount_used_query is not None else 0

        plan_limit_query = db.query(Plan.monthlyRateLimit).join(User).filter(User.id == user_id).scalar()

        monthly_limit = plan_limit_query if plan_limit_query is not None else 0

        if monthly_limit == 0:
            return 0

        credit_amount = monthly_limit - amount_used

        if with_limit:
            return {'credit_amount': credit_amount, 'monthly_limit': monthly_limit}

        return int(credit_amount)

    except Exception as e:
        print(f"Erreur API Python: {e}")
        return None

    finally:
        db.close()


def get_user_limit_per_user(user_id: int):
    db: Session | None = None

    try:
        db = SessionLocal()

        minute_limit_query = db.query(Plan.minuteRateLimit).join(User).filter(
            User.id == user_id
        ).scalar()

        if minute_limit_query is not None:
            return int(minute_limit_query)
        else:
            return None

    except Exception as ex:
        print(f"Erreur BDD lors de la récupération de la limite: {ex}")
        return None

    finally:
        db.close()


async def verify_internal_secret(x_internal_secret: Annotated[str, Header(alias="X-Internal-Secret")]):
    if not x_internal_secret or x_internal_secret != SYNC_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accès non autorisé. Jeton de synchronisation invalide."
        )
    return True
