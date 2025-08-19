import pickle
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(255), nullable=False)
    player2 = db.Column(db.String(255), nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    active = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, player1: str, player2: str, active: bool = False):
        self.player1 = player1
        self.player2 = player2
        self.active = active

    def set_match(self, match_object):
        self.data = pickle.dumps(match_object)

    def get_match(self):
        return pickle.loads(self.data)


class PlayerModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
