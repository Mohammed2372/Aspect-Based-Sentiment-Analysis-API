from fastapi import FastAPI

app = FastAPI(title="ABSA System API")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI is running 🚀"}
