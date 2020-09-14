import uvicorn  # type: ignore
from fastapi import FastAPI

from app.api import api
from app.db import database, engine, metadata

metadata.create_all(engine)
app = FastAPI()

app.include_router(api.api_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    await database.disconnect()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
