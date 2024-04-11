from sqlalchemy import Column, DateTime, func, JSON, String, Boolean, Integer

from database import Base


class Resume(Base):
    __tablename__ = 'copilot_api_resume'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    parsed_resume = Column(JSON)
    file = Column(String)
    uploaded_on = Column(DateTime(timezone=True), onupdate=func.now())
    parsed = Column(Boolean)
    is_valid_resume = Column(Boolean)
    resume_insight = Column(JSON)
    user_id = Column(Integer)
    submitted_form_data = Column(JSON)
    submitted_pdf_url = Column(String)
    email = Column(String)
    submitted_pdf_path = Column(String)

    def __str__(self):
        return self.uploaded_on.date()