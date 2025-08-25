import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_socketio import SocketIO, join_room, leave_room
from flask_wtf.csrf import CSRFProtect
from models import db, MatchModel, ValidationError
from tennis.match import TennisMatch
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
csrf = CSRFProtect()


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: The name of the configuration to use

    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


@app.errorhandler(ValidationError)
def validation_error(error):
    flash(str(error), "error")
    return redirect(url_for("home"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-match", methods=["GET", "POST"])
def create_match():
    """Handle match creation."""
    if request.method == "POST":
        try:
            # Validate input
            required_fields = [
                "player1",
                "player2",
                "num_games_to_win",
                "best_of_num_sets",
                "whos_serve",
                "with_AD",
            ]
            for field in required_fields:
                if field not in request.form:
                    raise ValidationError(f"Missing required field: {field}")

            player1 = request.form["player1"].strip()
            player2 = request.form["player2"].strip()

            try:
                num_games_to_win = int(request.form["num_games_to_win"])
                best_of_num_sets = int(request.form["best_of_num_sets"])
                if num_games_to_win < 1 or best_of_num_sets < 1:
                    raise ValueError("Game and set counts must be positive")
            except ValueError as e:
                raise ValidationError(str(e))

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

            logger.info(
                f"Created new match {match_model.id} between {player1} and {player2}"
            )
            flash("Match created successfully!", "success")
            return redirect(url_for("edit_match", match_id=match_model.id))

        except ValidationError as e:
            flash(str(e), "error")
            return redirect(url_for("create_match"))
        except Exception as e:
            logger.error(f"Error creating match: {str(e)}")
            db.session.rollback()
            flash("An error occurred while creating the match", "error")
            return redirect(url_for("create_match"))

    return render_template("creatematch.html")


@app.route("/matches", methods=["GET"])
def view_matches():
    matches = MatchModel.query.order_by(MatchModel.date_created.desc()).all()
    return render_template("matches.html", matches=matches)


@app.route("/match/<int:match_id>/edit", methods=["GET"])
def edit_match(match_id):
    matchmodel = MatchModel.query.get(match_id)
    if not matchmodel:
        return jsonify({"status": "error", "message": "Match not found"}), 404

    tennis_match = matchmodel.get_match()
    return render_template(
        "editmatch.html", tennis_match=tennis_match, match_id=match_id
    )


@app.route("/match/<int:match_id>")
def view_match(match_id):
    matchmodel = MatchModel.query.get(match_id)
    if not matchmodel:
        return "Match not found", 404

    tennis_match = matchmodel.get_match()
    return render_template("viewmatch.html", tennis_match=tennis_match)


# SocketIO events
@socketio.on("join_match_room")
def handle_join_room(data):
    match_id = data.get("match_id")
    if match_id:
        join_room(f"match_{match_id}")


@socketio.on("leave_match_room")
def handle_leave_room(data):
    match_id = data.get("match_id")
    if match_id:
        leave_room(f"match_{match_id}")


if __name__ == "__main__":
    socketio.run(app, debug=True)
