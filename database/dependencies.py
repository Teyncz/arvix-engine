from connection import SessionLocal, FrontSessionLocal
from sqlalchemy.orm import Session
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_front_db() -> Generator[Session, None, None]:
    db = FrontSessionLocal()
    try:
        yield db
    finally:
        db.close()