from fastapi import FastAPI

import uvicorn

app = FastAPI(title="ABSA System API")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI is running 🚀"}


if __name__ == "__main__":
    # use web server uvicorn to run app.app:app (folder.file:variable)
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
