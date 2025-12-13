from datetime import datetime
from pydantic import BaseModel
from typing import List


# input
class AnalyzeRequest(BaseModel):
    text: str


# output
class AspectResult(BaseModel):
    aspect: str
    sentiment: str
    confidence: float


class AnalyzeResponse(BaseModel):
    text: str
    results: List[AspectResult]


class FileUploadResponse(BaseModel):
    session_id: str
    file_name: str
    total_items: int
    message: str


# represent one row of review in history
class RecordSchemas(BaseModel):
    id: str
    original_text: str
    results: List[AspectResult]

    class Config:
        from_attributes = True


# represents file/session status
class SessionSchema(BaseModel):
    id: str
    status: str
    created_at: datetime
    total_items: int

    class Config:
        from_attributes = True


# detailed view
class SessionDetailSchema(SessionSchema):
    records: List[RecordSchemas]
