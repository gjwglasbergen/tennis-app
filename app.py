from flask import Flask
from flask_socketio import SocketIO
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


@app.route("/match")
def get_match():
    return "Hier komt een match"


if __name__ == "__main__":
    socketio.run(app, debug=True)
