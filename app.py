from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "tennisgoof"

socketio = SocketIO(app)


@app.route("/")
def home():
    return "Hello world test socket"


@app.route("/create-match")
def create_match():
    return "Hier kun je een match aanmaken"


@app.route("/match/<int:match_id>")
def get_match(match_id):
    return f"Dit is de link naar match {match_id}"


if __name__ == "__main__":
    socketio.run(app, debug=True)
