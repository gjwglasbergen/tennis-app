from flask import Flask, render_template
from flask_socketio import SocketIO
from models import db, MatchModel
from tennis.match import TennisMatch

app = Flask(__name__)
app.config["SECRET_KEY"] = "tennisgoof"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../data/app.db"

db.init_app(app)

with app.app_context():
    db.create_all()

socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-match")
def create_match():
    return render_template("creatematch.html")


@app.route("/matches")
def view_matches():
    return "Hier kun je wedstrijden selecteren en bekijken"


@app.route("/match/<int:match_id>")
def get_match(match_id):
    return f"Dit is de link naar match {match_id}"


if __name__ == "__main__":
    socketio.run(app, debug=True)
