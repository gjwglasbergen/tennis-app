from flask import Flask, render_template, request, redirect, url_for
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


@app.route("/create-match", methods=["GET", "POST"])
def create_match():
    if request.method == "POST":
        player1 = request.form["player1"]
        player2 = request.form["player2"]
        num_games_to_win = int(request.form["num_games_to_win"])
        best_of_num_sets = int(request.form["best_of_num_sets"])
        whos_serve_player = request.form["whos_serve"]
        whos_serve = request.form[whos_serve_player]
        with_AD = request.form["with_AD"]

        matchFormat = {
            "num_games_to_win": num_games_to_win,
            "best_of_num_sets": best_of_num_sets,
            "whos_serve": whos_serve,
            "with_AD": with_AD,
        }

        tennis_match = TennisMatch(
            player1=player1, player2=player2, matchFormat=matchFormat
        )

        match_model = MatchModel(player1=player1, player2=player2)
        match_model.set_match(tennis_match)
        db.session.add(match_model)
        db.session.commit()
        return redirect(url_for("edit_match", match_id=match_model.id))

    return render_template("creatematch.html")


@app.route("/matches")
def view_matches():
    return "Hier kun je wedstrijden selecteren en bekijken"


@app.route("/edit_match/<int:match_id>")
def edit_match(match_id):
    return f"Edit match {match_id}"


@app.route("/match/<int:match_id>")
def view_match(match_id):
    matchmodel = MatchModel.query.get(match_id)
    if matchmodel:
        tennis_match = matchmodel.get_match()

    return render_template("viewmatch.html", tennis_match=tennis_match)


if __name__ == "__main__":
    socketio.run(app, debug=True)
