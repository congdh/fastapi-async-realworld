import uvicorn  # type: ignore
from fastapi import FastAPI

from app.api import api

app = FastAPI()

app.include_router(api.api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
