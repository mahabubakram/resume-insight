# build a schema using pydantic
import json

from pydantic import BaseModel, EmailStr


class Resume(BaseModel):
    parsed_resume: json
    file: str
    parsed: bool
    is_valid_resume: bool
    resume_insight: json
    user_id: int
    submitted_form_data: json
    submitted_pdf_url: str
    email: str
    submitted_pdf_path: str

    class Config:
        orm_mode = True

