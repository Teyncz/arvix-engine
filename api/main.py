from fastapi import FastAPI, Response

from api.routers.v1.crypto import router as crypto_overview_router

app = FastAPI(version="0.1.0",)

app.include_router(crypto_overview_router, prefix="/v1/crypto")


@app.get("/")
def read_root():
    return Response("Hello World")
