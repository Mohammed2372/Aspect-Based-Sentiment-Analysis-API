from typing import List
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Request,
    UploadFile,
    File,
    BackgroundTasks,
)
from io import StringIO
from requests import Session

import pandas as pd
import uuid


from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    FileUploadResponse,
    SessionDetailSchema,
    SessionSchema,
)
from app.api import deps
from app.models.user import User
from app.models.analysis import (
    AnalysisRecord,
    AnalysisSession,
    AspectResult as AspectResultModel,
)
from app.db.session import session_local


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


# helper function to process file in background
def process_csv_file(
    content: bytes,
    session_id: str,
    model,
    db_session_factory,
):
    # create new db session for this background task
    db = db_session_factory()

    try:
        # read csv file
        df = pd.read_csv(StringIO(content.decode("utf-8")))

        # column with text
        text_col = next(
            (col for col in df.columns if col.lower() in ["text", "review", "content"]),
            None,
        )

        # fallback if column name is not in previous list
        if not text_col:
            text_col = df.columns[0]

        # analyze rows
        for _, row in df.iterrows():
            text = str(row[text_col])

            # run ai model
            ai_results = model.predict(text)

            # generate uuid manually
            new_record_id = str(uuid.uuid4())

            # save record
            record = AnalysisRecord(
                id=new_record_id, session_id=session_id, original_text=text
            )
            db.add(record)
            db.commit()

            # save results
            for res in ai_results:
                aspect = AspectResultModel(
                    record_id=new_record_id,
                    aspect=res["aspect"],
                    sentiment=res["sentiment"],
                    confidence=res["confidence"],
                )
                db.add(aspect)
        # flush every row so memory does not explode
        db.flush()

        # update session status
        session = (
            db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        )
        session.status = "completed"
        db.commit()

    except Exception as e:
        print(f"🔥 WORKER ERROR: {e}")
        db.rollback()
        try:
            session = (
                db.query(AnalysisSession)
                .filter(AnalysisSession.id == session_id)
                .first()
            )
            if session:
                session.status = "Failed"
                db.commit()
                print("❌ Session marked as FAILED.")
        except Exception as update_error:
            print(f"💀 Critical Failure updating status: {update_error}")
    finally:
        db.close()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_csv(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    # read file content
    content = await file.read()

    # create a session entry in db
    session_entry = AnalysisSession(
        user_id=current_user.id,
        session_type="FILE",
        status="Processing",
        total_items=0,
    )
    db.add(session_entry)
    db.commit()
    db.refresh(session_entry)

    # trigger background task
    model = request.app.state.absa_model

    background_tasks.add_task(
        process_csv_file,
        content,
        session_entry.id,
        model,
        session_local,
    )

    return {
        "session_id": session_entry.id,
        "file_name": file.filename,
        "total_items": 0,
        "message": "File uploaded! Processing started in background.",
    }


# get list of all uploads
@router.get("/history", response_model=List[SessionSchema])
def get_user_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    # retrieve current user sessions only
    sessions = (
        db.query(AnalysisSession)
        .filter(AnalysisSession.user_id == current_user.id)
        .order_by(AnalysisSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return sessions


# get result for one upload
@router.get("/history/{session_id}", response_model=SessionDetailSchema)
def get_session_details(
    session_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    # find session
    session = (
        db.query(AnalysisSession)
        .filter(
            AnalysisSession.id == session_id,
            AnalysisSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session
