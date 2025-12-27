from dataclasses import dataclass, field
from typing import List, Optional
from .config import MatchConfig
from .set import Set

@dataclass
class TennisMatch:
    p1_name: str
    p2_name: str
    config: MatchConfig
    sets: List[Set] = field(default_factory=list)
    current_set_index: int = 0
    winner: Optional[str] = None
    
    # State tracking
    p1_sets_won: int = 0
    p2_sets_won: int = 0
    server_is_p1: bool = True # Initial server
    
    def __post_init__(self):
        if not self.sets:
            self.start_new_set()

    def start_new_set(self):
        new_set = Set(self.config)
        self.sets.append(new_set)

    @property
    def current_set(self) -> Set:
        return self.sets[self.current_set_index]

    def score_point(self, p1_won_point: bool):
        if self.winner:
            return # Match over

        set_won = self.current_set.score_point(self.server_is_p1, p1_won_point)
        
        # Update server for next point?
        # Tiebreaker needs special rotation logic (1, 2, 2, 2...)
        # Standard game: Server stays same for whole game.
        # Only switch server if Game Finished (which Set handles, but Match needs to know).
        # Wait, Set.score_point handles the game transition internally. 
        # We need to observe if the game changed.
        
        # Actually proper logic:
        # Match tracks who is serving for the *current game*.
        # Set.score_point returns True if set finished. 
        # If set finished -> Next set starts. 
        # If only game finished -> Switch server.
        
        # To do this cleanly, strict dependency direction: Match -> Set -> Game.
        # Match needs to ask Set "Did the game just finish?".
        # Or better separate concerns: Match handles rotation.
        
        # Simplification for now:
        # If the set's game count changed, or if it's a new set, switch server.
        # But tiebreaker point-by-point rotation is tricky here.
        
        # Let's rely on checking if the 'current_game' object changed or reset.
        pass

    def point_won_by(self, player_num: int):
        if self.winner:
            return
            
        p1_wins = (player_num == 1)
        
        # Snapshot state before scoring
        prev_game = self.current_set.current_game
        prev_p1_games = self.current_set.p1_games
        prev_p2_games = self.current_set.p2_games
        
        # Perform Score
        set_won = self.current_set.score_point(self.server_is_p1, p1_wins)
        
        # Logic for Server Rotation
        if set_won:
            self._handle_set_win()
            # Switch server for next set (simplified, usually loser of last game serves first? or continuous rotation?)
            # Rule: Server of the first game of a set is the one who received in the last game of previous set.
            self.server_is_p1 = not self.server_is_p1
        else:
            # Set continues. Did game finish?
            curr_p1_games = self.current_set.p1_games
            curr_p2_games = self.current_set.p2_games
            
            game_finished = (curr_p1_games != prev_p1_games) or (curr_p2_games != prev_p2_games)
            
            if game_finished:
                 self.server_is_p1 = not self.server_is_p1
            elif self.current_set.current_game.is_tiebreaker:
                # Tiebreaker rotation: 
                # (Point 1 served by A, 2-3 by B, 4-5 by A...)
                # Sum of points decides.
                points_sum = self.current_set.current_game.p1_tiebreaker_points + self.current_set.current_game.p2_tiebreaker_points
                # Pattern: 1, 2, 2, 2, 2...
                # Change server if (sum % 2 == 1) ? No.
                # Points: 0 (A), 1 (B), 2 (B), 3 (A), 4 (A), 5 (B)... 
                # Switch after every odd sum? 
                # After 1st point (sum=1). After 3rd point (sum=3). After 5th point.
                if points_sum % 2 == 1:
                     self.server_is_p1 = not self.server_is_p1

    def _handle_set_win(self):
        w = self.current_set.winning_player
        if w == 1:
            self.p1_sets_won += 1
        else:
            self.p2_sets_won += 1
            
        if self.p1_sets_won >= self.config.sets_to_win:
            self.winner = self.p1_name
        elif self.p2_sets_won >= self.config.sets_to_win:
            self.winner = self.p2_name
        else:
            self.current_set_index += 1
            self.start_new_set()

    def to_json(self):
        """Serialize state for frontend/socket."""
        current_game = self.current_set.current_game
        return {
            "p1_name": self.p1_name,
            "p2_name": self.p2_name,
            "p1_sets": self.p1_sets_won,
            "p2_sets": self.p2_sets_won,
            "current_set_score": self.current_set.get_score(),
            "p1_games": self.current_set.p1_games,
            "p2_games": self.current_set.p2_games,
            "p1_points": current_game.get_display_score().split('-')[0] if current_game else "0",
            "p2_points": current_game.get_display_score().split('-')[1] if current_game else "0",
            "server": 1 if self.server_is_p1 else 2,
            "winner": self.winner,
            "is_tiebreaker": current_game.is_tiebreaker if current_game else False
        }
