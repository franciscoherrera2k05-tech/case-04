import hashlib
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

def hash_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = Field(None)
    submission_id: Optional[str] = Field(None)
  

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v

    def to_stored_record(self) -> dict:
        hashed_email = hash_sha256(self.email)
        hashed_age = hash_sha256(str(self.age))  # convert int to string

        if self.submission_id:
            sid = self.submission_id   # use provided submission_id
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H")
            sid = hash_sha256(self.email + timestamp)  # generate server-sid

        return {
            "name": self.name,
            "email": hashed_email,
            "age": hashed_age,
            "consent": self.consent,
            "rating": self.rating,
            "comments": self.comments,
            "user_agent": self.user_agent,
            "submission_id": sid,
            "received_at": datetime.now(timezone.utc).isoformat()
        }
    


        
#Good example of inheritance
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
