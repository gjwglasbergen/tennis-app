import os
import logging
import json
from datetime import datetime, timezone, timedelta
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
            with_AD = request.form["with_AD"] == "True"  # Convert string to boolean

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
    
    # Update active status based on 30 minute timeout
    now = datetime.now(timezone.utc)
    for match in matches:
        match_data = match.get_match()
        # Check if match has a winner
        if match_data.get('winner', ''):
            if match.active:
                match.active = False
        # Check if last update was more than 30 minutes ago
        elif match.active and match.last_updated:
            # Make sure last_updated is timezone aware
            last_updated = match.last_updated
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=timezone.utc)
            
            time_diff = now - last_updated
            if time_diff > timedelta(minutes=30):
                match.active = False
    
    db.session.commit()
    return render_template("matches.html", matches=matches)


@app.route("/match/<int:match_id>/edit", methods=["GET"])
def edit_match(match_id):
    matchmodel = MatchModel.query.get(match_id)
    if not matchmodel:
        return jsonify({"status": "error", "message": "Match not found"}), 404

    tennis_match = matchmodel.get_match()
    has_backup = matchmodel.backup_data is not None
    return render_template(
        "editmatch.html", tennis_match=tennis_match, match_id=match_id, has_backup=has_backup
    )


@app.route("/match/<int:match_id>")
def view_match(match_id):
    matchmodel = MatchModel.query.get(match_id)
    if not matchmodel:
        return "Match not found", 404

    tennis_match = matchmodel.get_match()
    return render_template("viewmatch.html", tennis_match=tennis_match, match_id=match_id)


@app.route("/match/<int:match_id>/data", methods=["GET"])
def get_match_data(match_id):
    """Get match data as JSON for live updates."""
    matchmodel = MatchModel.query.get(match_id)
    if not matchmodel:
        return jsonify({"status": "error", "message": "Match not found"}), 404
    
    tennis_match = matchmodel.get_match()
    return jsonify({
        "status": "success",
        "match": tennis_match,
        "active": matchmodel.active
    })


@app.route("/match/<int:match_id>/add-point", methods=["POST"])
def add_point(match_id):
    """Add a point to a player."""
    try:
        matchmodel = MatchModel.query.get(match_id)
        if not matchmodel:
            return jsonify({"status": "error", "message": "Match not found"}), 404

        data = request.get_json()
        player = data.get("player")
        
        if not player:
            return jsonify({"status": "error", "message": "Player required"}), 400

        # Get the current match state
        from tennis.match import TennisMatch
        match_dict = matchmodel.get_match()
        
        # Recreate TennisMatch object
        tennis_match = TennisMatch(
            player1=match_dict["player1"],
            player2=match_dict["player2"],
            matchFormat=match_dict["matchFormat"]
        )
        tennis_match.__dict__.update(match_dict)
        
        # Backup current state before adding point (save as JSON string)
        matchmodel.backup_data = matchmodel.data
        
        # Add the point
        tennis_match.win_point(player)
        
        # Update match state
        matchmodel.set_match(tennis_match)
        matchmodel.last_updated = datetime.now(timezone.utc)
        
        # Check if match is won
        match_dict_updated = matchmodel.get_match()
        if match_dict_updated.get('winner', ''):
            matchmodel.active = False
        else:
            matchmodel.active = True
        
        db.session.commit()
        
        # Get updated state
        updated_match = matchmodel.get_match()
        
        logger.info(f"Point added for {player} in match {match_id}")
        return jsonify({"status": "success", "match": updated_match})
        
    except Exception as e:
        logger.error(f"Error adding point: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/match/<int:match_id>/undo", methods=["POST"])
def undo_point(match_id):
    """Undo the last point."""
    try:
        matchmodel = MatchModel.query.get(match_id)
        if not matchmodel:
            return jsonify({"status": "error", "message": "Match not found"}), 404

        if not matchmodel.backup_data:
            return jsonify({"status": "error", "message": "No backup available"}), 400

        # Simply restore the backup data directly
        backup_data = matchmodel.backup_data
        matchmodel.data = backup_data
        matchmodel.backup_data = None  # Clear backup after use
        db.session.commit()
        
        # Get updated state
        updated_match = matchmodel.get_match()
        
        logger.info(f"Undo performed for match {match_id}")
        return jsonify({"status": "success", "match": updated_match})
        
    except Exception as e:
        logger.error(f"Error undoing point: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


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
