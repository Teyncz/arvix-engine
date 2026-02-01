from datetime import datetime, timezone

from database.connection import SessionLocal
from database.models import ApiKey
from sqlalchemy import desc


def get_user_usage(key_id, key, name, user_id):
    db = SessionLocal()

    new_key = ApiKey(
        id=key_id,
        userId=user_id,
        name=name,
        key=key,
        status=True,
    )

    db.add(new_key)

    try:
        db.commit()
        db.refresh(new_key)
        return True

    except Exception as e:
        db.rollback()
        return False

