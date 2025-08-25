import json
from typing import Any, Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()


class ValidationError(Exception):
    """Custom exception for data validation errors."""

    pass


class MatchModel(db.Model):
    """Model representing a tennis match."""

    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(255), nullable=False, index=True)
    player2 = db.Column(db.String(255), nullable=False, index=True)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc), index=True
    )
    active = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.Text, nullable=False)  # Store JSON instead of pickle

    def __init__(self, player1: str, player2: str, active: bool = False):
        """Initialize a new match.

        Args:
            player1: Name of the first player
            player2: Name of the second player
            active: Whether the match is currently active

        Raises:
            ValidationError: If player names are empty or identical
        """
        if not player1 or not player2:
            raise ValidationError("Player names cannot be empty")
        if player1 == player2:
            raise ValidationError("Players must be different")

        self.player1 = player1
        self.player2 = player2
        self.active = active

    def set_match(self, match_object: Any) -> None:
        """Store the match state as JSON.

        Args:
            match_object: The tennis match object to serialize
        """
        try:
            self.data = json.dumps(match_object.__dict__)
        except (TypeError, AttributeError) as e:
            raise ValidationError(f"Invalid match object: {str(e)}")

    def get_match(self) -> dict:
        """Retrieve the match state.

        Returns:
            dict: The deserialized match state

        Raises:
            ValidationError: If the stored data is invalid
        """
        try:
            return json.loads(self.data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid match data: {str(e)}")


class PlayerModel(db.Model):
    """Model representing a tennis player."""

    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Indexes
    __table_args__ = (db.Index("idx_player_name_surname", "name", "surname"),)

    @property
    def full_name(self) -> str:
        """Get the player's full name."""
        return f"{self.name} {self.surname}"

    def __init__(self, name: str, surname: str):
        """Initialize a new player.

        Args:
            name: Player's first name
            surname: Player's last name

        Raises:
            ValidationError: If name or surname is empty
        """
        if not name or not surname:
            raise ValidationError("Name and surname cannot be empty")

        self.name = name.strip()
        self.surname = surname.strip()

    def __repr__(self) -> str:
        """String representation of the player."""
        return f"<Player {self.full_name}>"
