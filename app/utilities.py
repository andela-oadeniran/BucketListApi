from bucketlist import db


def save(obj):
    # adds a valid instance to the session
    try:
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
