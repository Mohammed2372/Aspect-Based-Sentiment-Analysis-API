from fastapi import FastAPI

import uvicorn

from app.api.v1.endpoints import auth


app = FastAPI(title="ABSA System API")
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

if __name__ == "__main__":
    # use web server uvicorn to run app.app:app (folder.file:variable)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
