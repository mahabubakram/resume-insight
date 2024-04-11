import logging
import sys

from fastapi import FastAPI, Depends
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_utilities import repeat_every
from supabase import Client, create_client

import database
import models
from logger import get_logger
from tasks import insight_task

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=database.SQLALCHEMY_DATABASE_URL)
models.Base.metadata.create_all(bind=database.engine)

local_logger = get_logger(__name__)


@app.get("/")
async def root():
    db = database.SessionLocal()
    resumes = db.query(models.Resume).filter(models.Resume.parsed == False).all()
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event("startup")
@repeat_every(seconds=300)
async def print_hello():
    local_logger.info("start Parsing")
    print("Start parsing")
    db = database.SessionLocal()
    insight_task(db)
    print("End parsing")
    local_logger.info("End Parsing")
    return None
