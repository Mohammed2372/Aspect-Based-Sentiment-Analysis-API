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