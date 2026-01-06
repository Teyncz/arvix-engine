from datetime import datetime, timezone

from api.schemas import UserUsage
from database.connection import SessionLocal
from database.models import ApiKey, User, UserStatus, RequestsUsage

def add_api_key(key_id, key, name, user_id):
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


def edit_api_key(key_id, status, name):
    db = SessionLocal()

    update_data = {}

    if status is not None:
        update_data['status'] = status

    if name is not None:
        update_data['name'] = name

    if not update_data:
        return None

    try:
        db = SessionLocal()

        update_data['updatedAt'] = datetime.now(timezone.utc)

        result = db.query(ApiKey).filter(ApiKey.id == key_id).update(
            update_data,
            synchronize_session="fetch"
        )

        db.commit()

        if result > 0:
            updated_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
            return updated_key
        else:
            return None

    except Exception as e:
        print(f"Erreur BDD lors de l'édition de la clé {key_id}: {e}")
        if db:
            db.rollback()
        return None

    finally:
        if db:
            db.close()

def delete_api_key(key_id):
    db = SessionLocal()

    try:
        db.query(ApiKey).filter(ApiKey.id == key_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        if db:
            db.close()

def add_user(user_id, email) :
    db = SessionLocal()

    try:
        new_user = User(
            id=user_id,
            email=email,
            status=UserStatus.VERIFIED,
            planId=1
        )
        db.add(new_user)

        new_user_usage = RequestsUsage(
            user_id=user_id,
            requests_number=0
        )
        db.add(new_user_usage)

        db.commit()
        db.refresh(new_user)
        return True

    except Exception as e:
        db.rollback()
        return False

    finally:
        db.close()