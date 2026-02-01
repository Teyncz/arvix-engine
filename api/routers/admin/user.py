from fastapi import APIRouter, HTTPException, Depends
from services.sync_service import add_api_key, edit_api_key, add_user
from database.crud import get_historical_rates
from api.schemas import UserUsage, UserSyncSchema
from api.dependencies import verify_internal_secret, get_credits_amount
from typing import Annotated
import os

SYNC_API_SECRET = os.getenv("SYNC_API_SECRET")

router = APIRouter()

@router.post("/usage")
def get_user_usage(payload: UserUsage,):
    usage = get_credits_amount(payload.user_id, True)
    if not usage:
        raise HTTPException(status_code=400, detail="Failed to get user usage")
    return {
        "status": "success",
        "data" : usage,
    }

@router.post("/sync/add")
def create_user(payload: UserSyncSchema,):
    newUser = add_user(payload.user_id, payload.email)
    if not newUser:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {
        "status": "success",
    }
