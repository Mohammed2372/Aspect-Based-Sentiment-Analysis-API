from fastapi import APIRouter, HTTPException, Depends, Request


from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.api import deps
from app.models.user import User


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(
    request: Request,
    payload: AnalyzeRequest,
    current_user: User = Depends(deps.get_current_user),
):
    # retrieve the model from the app state
    model = request.app.state.absa_model

    if not model:
        raise HTTPException(status_code=500, detail="AI Model is not loaded yet.")

    # run inference
    results = model.predict(payload.text)

    return {"text": payload.text, "results": results}
