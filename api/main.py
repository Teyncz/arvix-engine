from collections import defaultdict
import time
from typing import Dict
from fastapi import FastAPI, Response, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from api.dependencies import check_api_key
from api.routers.v1.crypto import router as crypto_overview_router

app = FastAPI(version="0.1.0")

app.include_router(crypto_overview_router, prefix="/v1/crypto", dependencies=[Depends(check_api_key)])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "error": exc.detail
        }
    )

class Middleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = defaultdict(list)
        self.limit = 10
        self.window_size = 60

    @staticmethod
    async def log_message(message: str):
        print(message)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if not self.rate_limit_records[client_ip]:
            self.rate_limit_records[client_ip].append(current_time)
        elif current_time - self.rate_limit_records[client_ip][0] > self.window_size :
            self.rate_limit_records[client_ip].clear()
            self.rate_limit_records[client_ip].append(current_time)
        else :
            if len(self.rate_limit_records[client_ip]) >= self.limit:
                time_left = self.window_size - (current_time - self.rate_limit_records[client_ip][0])
                return JSONResponse(status_code=429, content={"status": "ERROR", "error": f"Rate limit reached | {format(round(time_left, 1))} seconds left"})
            else :
                self.rate_limit_records[client_ip].append(current_time)

        path = request.url.path
        await self.log_message(f"Request to {path}")

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        await self.log_message(f"Response for path {path} took {process_time} seconds")

        return response


app.add_middleware(Middleware)
