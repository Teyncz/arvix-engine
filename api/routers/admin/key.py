from fastapi import APIRouter, HTTPException, Depends
from services.sync_service import add_api_key, edit_api_key, delete_api_key
from database.crud import get_historical_rates
from api.schemas import TickerDataResponse, TickerAggregateResponse, ApiKeySyncSchema, EditApiKeySyncSchema, DeleteApiKeySyncSchema
from api.dependencies import verify_internal_secret
from typing import Annotated
import os

SYNC_API_SECRET = os.getenv("SYNC_API_SECRET")

router = APIRouter()

@router.post("/sync/add")
def sync_new_key(payload: ApiKeySyncSchema,):
    newKey = add_api_key(payload.key_id, payload.key, payload.name, payload.user_id)
    if not newKey:
        raise HTTPException(status_code=400, detail="Key creation failed")
    return {
        "status": "success"
    }

@router.post("/sync/edit")
def sync_key_edition(payload: EditApiKeySyncSchema,):
    newKey = edit_api_key(payload.key_id, payload.status, payload.name)
    if not newKey:
        raise HTTPException(status_code=400, detail="Key creation failed")
    return {
        "status": "success"
    }

@router.post("/sync/delete")
def sync_key_edition(payload: DeleteApiKeySyncSchema,):
    deletedKey = delete_api_key(payload.key_id)
    if not deletedKey:
        raise HTTPException(status_code=400, detail="Key deletion failed")
    return {
        "status": "success"
    }
