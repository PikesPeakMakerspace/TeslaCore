from . import db

# TODO: Add when token was set to expire, for a future cleanup script
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)