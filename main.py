from typing import Any, Generator
from fastapi import FastAPI
from contextlib import asynccontextmanager

import uvicorn

from app.api.v1.endpoints import auth
from app.services.ai_model import ABSAModel


# global dictionary to hold models
ai_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ai_models["absa"] = ABSAModel("model/absa_bert_model")
    yield
    ai_models.clear()


app = FastAPI(title="ABSA System API", lifespan=lifespan)
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
