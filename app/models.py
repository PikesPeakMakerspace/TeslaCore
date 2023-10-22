#TODO: I see this moving and I wonder how it relates to other db types or if the models here will work elsewhere.
from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    #TODO: I don't recommend integers as primary key, yet let's keep it for the moment while following tutorial.
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))