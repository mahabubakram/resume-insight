from psycopg2 import OperationalError
from sqlalchemy.orm import Session
from supabase import Client, create_client

import models
from resumeParsing import *

supabase: Client = create_client("https://kexddhjgsuypqmvxhnoy.supabase.co",
                                 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtleGRkaGpnc3V5cHFtdnhobm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDY3MTY0NjYsImV4cCI6MjAyMjI5MjQ2Nn0.UYW6y60XM1-9FZ-a_vvbX_iLsFhG8plVrVq6z6VFHMA")


def insight_task(db: Session):
    try:
        resumes = db.query(models.Resume).filter(Resume.parsed == False).all()
    except OperationalError as err:
        return err
    print("Total Resume Found to Parse: " + str(len(resumes)))
    # resumes = supabase.table("copilot_api_resume").select("*").eq('parsed', 'False').execute()
    for resume in resumes:
        file_response = download_file(resume)
        parsed_resume = resume_parser(file_response)

        resume.parsed_resume = json.loads(parsed_resume)
        resume.is_valid_resume = is_resume(parsed_resume)
        if resume.is_valid_resume:
            resume.resume_insight = json.loads(gpt_resume_insight(parsed_resume))
        resume.parsed = True
        db.add(resume)
        db.commit()
        #db.refresh(resume)
        print("DB update done")
    return None
