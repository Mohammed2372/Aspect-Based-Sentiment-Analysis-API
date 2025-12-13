from fastapi import FastAPI
from contextlib import asynccontextmanager

import uvicorn

from app.api.v1.endpoints import auth, analysis
from app.services.ai_model import ABSAModel


# global dictionary to hold models
ai_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.absa_model = ABSAModel()
    yield
    app.state.absa_model = None


# app
app = FastAPI(title="ABSA System API", lifespan=lifespan)

# routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
