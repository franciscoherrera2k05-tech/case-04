from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SurveySubmission(BaseModel):
    name: str
    email: EmailStr
    age: int
    consent: bool
    rating: int
    comments: Optional[str] = None
    user_agent: Optional[str] = None
    submission_id: Optional[str] = None

class StoredSurveyRecord(BaseModel):
    name: str
    consent: bool
    rating: int
    comments: str
    user_agent: str
    submission_id: str
    hashed_email: str
    hashed_age: str
    received_at: datetime
    ip: str