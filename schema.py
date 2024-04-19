# build a schema using pydantic
import json

from pydantic import BaseModel


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


class Variant(BaseModel):
    suggested_insight: json
    target_job_title: str
    target_job_title: str
    detected_gaps: json
    user_id: int
    email: str
    based_on_variant_id: int
    confirmed_insight: json
    title: str
    base_insight: json
    job_insight: json
    gap_on_suggested_and_base: json

    class Config:
        orm_mode = True
