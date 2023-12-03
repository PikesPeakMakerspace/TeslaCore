from app.database import db
from app.models import TokenBlocklist
from datetime import datetime, timedelta


def remove_old_tokens():
    from app.app import app
    with app.app_context():
        forty_days = timedelta(days=40)
        forty_days_ago = datetime.now() - forty_days
        query = TokenBlocklist.__table__.delete().where(
            TokenBlocklist.created_at < forty_days_ago
        )
        db.session.execute(query)
        db.session.commit()
        print('old jwt tokens removed')
