from fastapi import FastAPI
from loguru import logger

from app.api import api
from app.db import database

app = FastAPI()

app.include_router(api.api_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    logger.info("Connect to database")
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Disconnect to database")
    await database.disconnect()
