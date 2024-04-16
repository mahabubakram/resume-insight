from fastapi import FastAPI, Depends, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_utilities import repeat_every

import database
import models
from logger import get_logger
from tasks import insight_task

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

app.add_middleware(DBSessionMiddleware, db_url=database.SQLALCHEMY_DATABASE_URL)
models.Base.metadata.create_all(bind=database.engine)

api_key_header = APIKeyHeader(name="X-API-Key")
apiKey = "f500f6d57eba1a99bd6f1cf53e314e9750c5aa9811a90dbb7d6d77866de72708103956b424920792d6e82b73e4a748f7eb0604c156cea3d6dd4ddf9391eb1dc6"

local_logger = get_logger(__name__)


@app.get("/")
async def root():
    db = database.SessionLocal()
    resumes = db.query(models.Resume).filter(models.Resume.parsed == False).all()
    return {"message": "Hello World"}


def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == apiKey:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )

@app.get("/hello/{name}")
async def say_hello(name: str, commons: dict = Depends(get_api_key)):
    return {"message": f"Hello {name}"}


@app.get("/run-resume-insight")
async def run_resume_insight_task(commons: dict = Depends(get_api_key)):
    db = database.SessionLocal()
    local_logger.info("start Parsing")
    insight_task(db)
    local_logger.info("End Parsing")
    return {"message": "ran the task of resume insight generation"}

# @app.on_event("startup")
# @repeat_every(seconds=300)
# async def print_hello():
#     local_logger.info("start Parsing")
#     print("Start parsing")
#     db = database.SessionLocal()
#     insight_task(db)
#     print("End parsing")
#     local_logger.info("End Parsing")
#     return None
