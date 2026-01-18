from collections import defaultdict
import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from database.models import RequestsUsage
from api.dependencies import check_api_key, get_client_by_api_key, get_credits_amount, get_user_limit_per_user, verify_internal_secret
from api.routers.v1.crypto import router as crypto_overview_router
from api.routers.v1.indices import router as indices_overview_router
from api.routers.v1.currency import router as currency_overview_router
from api.routers.admin.key import router as admin_key_router
from api.routers.admin.user import router as admin_user_router
from database.connection import SessionLocal
from core.exceptions import AppException

app = FastAPI(version="0.1.0")

app.include_router(admin_key_router, prefix="/admin/key", dependencies=[Depends(verify_internal_secret)])
app.include_router(admin_user_router, prefix="/admin/user", dependencies=[Depends(verify_internal_secret)])
app.include_router(crypto_overview_router, prefix="/v1/crypto", dependencies=[Depends(check_api_key)])
app.include_router(indices_overview_router, prefix="/v1/indices", dependencies=[Depends(check_api_key)])
app.include_router(currency_overview_router, prefix="/v1/currency", dependencies=[Depends(check_api_key)])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "error": exc.detail
        }
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "error": exc.message
        }
    )

class Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.api_key_to_user = {}
        self.user_credits_amount = {}
        self.user_limit_per_minute = {}
        self.request_log_counts = defaultdict(int)
        self.window_size = 60
        self.worker_task = asyncio.create_task(self.worker())
        self.last_batch_time = time.time()

    @staticmethod
    async def log_message(message: str):
        print(message)

    async def worker(self):
        while True:
            if self.request_log_counts:
                batch_dict = self.request_log_counts.copy()
                self.request_log_counts.clear()
                batch = [{"user_id": user_id, "requests_number": count}
                         for user_id, count in batch_dict.items()]
                await self.insert_batch(batch)
            await asyncio.sleep(60)

    async def insert_batch(self, batch: list):
        db = SessionLocal()
        try:
            for entry in batch:
                user_id = entry["user_id"]
                count = entry["requests_number"]
                db.query(RequestsUsage).filter(RequestsUsage.user_id == user_id).update({
                    RequestsUsage.requests_number: RequestsUsage.requests_number + count
                })
            db.commit()
            self.last_batch_time = time.time()
            await self.log_message(f"Batch updated: {batch}")
        finally:
            db.close()

    async def dispatch(self, request: Request, call_next):
        #client_ip = request.client.host
        path = request.url.path

        PROTECTED_PREFIXES = ["/v1/"]

        is_protected = any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)

        if not is_protected:
            return await call_next(request)

        api_key = request.headers["Authorization"]
        user_id = None
        if api_key.startswith("Bearer "):
            api_key = api_key.split(" ")[1]
            if api_key not in self.api_key_to_user:
                user_id = get_client_by_api_key(api_key)
                self.api_key_to_user[api_key] = user_id
                await self.log_message(f"Api key {api_key}")
            else:
                user_id = self.api_key_to_user[api_key]

        current_time = time.time()

        if user_id:

            #Si le cache n'a pas encore enregistré l'API key
            if not self.request_log_counts[user_id]:

                # Récupère les crédits restant
                if self.user_credits_amount.get(user_id) is None:
                    self.user_credits_amount[user_id] = get_credits_amount(user_id)

                # Récupère le rate limite du plan de l'utilisateur
                if self.user_limit_per_minute.get(user_id) is None:
                    self.user_limit_per_minute[user_id] = get_user_limit_per_user(user_id)

                if self.user_credits_amount[user_id] > 0 :

                    if self.request_log_counts[user_id] >= self.user_limit_per_minute[user_id]:
                        time_left = self.window_size - (current_time - self.last_batch_time)
                        return JSONResponse(status_code=429, content={"status": "ERROR","error": f"Rate limit reached | {format(round(time_left, 1))} seconds left"})

                    self.request_log_counts[user_id] += 1
                    self.user_credits_amount[user_id] -= 1

                else:
                    return JSONResponse(status_code=429, content={"status": "ERROR", "error": f"Rate limit reached for this month"})

            # Si le cache connait déjà l'API key
            else :

                if self.request_log_counts[user_id] >= self.user_limit_per_minute[user_id]:
                    time_left = self.window_size - (current_time - self.last_batch_time)
                    return JSONResponse(status_code=429, content={"status": "ERROR", "error": f"Rate limit reached | {format(round(time_left, 1))} seconds left"})

                else :

                    if self.user_credits_amount[user_id] > 0:
                        self.request_log_counts[user_id] += 1
                        self.user_credits_amount[user_id] -= 1

                    else:
                        return JSONResponse(status_code=429, content={"status": "ERROR", "error": f"Rate limit reached for this month"})

        path = request.url.path
        await self.log_message(f"Request to {path}")
        #await self.log_message(f"{self.request_log}")
        #await self.log_message(f"{self.user_credits_amount}")
        await self.log_message(f"{self.request_log_counts}")

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        await self.log_message(f"Response for path {path} took {process_time} seconds")

        return response


app.add_middleware(Middleware)
