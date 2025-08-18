import pickle
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary, nullable=False)

    def set_match(self, match_object):
        self.data = pickle.dumps(match_object)

    def get_match(self):
        return pickle.loads(self.data)
