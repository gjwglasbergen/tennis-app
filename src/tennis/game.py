from dataclasses import dataclass, field
from typing import Optional, Literal
from .scoring.point_scorer import PointScorer, create_point_scorer, PointValue
from .config import MatchConfig

@dataclass
class Game:
    scorer: PointScorer
    server_points: int = 0
    receiver_points: int = 0
    is_tiebreaker: bool = False
    
    # Tiebreaker specific state
    p1_tiebreaker_points: int = 0
    p2_tiebreaker_points: int = 0
    
    @classmethod
    def create(cls, config: MatchConfig, is_tiebreaker: bool = False) -> 'Game':
        # Tiebreaker games don't use the standard Advantage/NoAdvantage scorer in the same way,
        # but for now we'll handle tiebreaker scoring logic directly in score_point or a dedicated TiebreakerScorer.
        # Minimal viable: Flag determines logic.
        scorer = create_point_scorer(config.advantage)
        return cls(scorer=scorer, is_tiebreaker=is_tiebreaker)

    def score_point(self, server_won: bool) -> bool:
        """
        Scores a point. Returns True if the game is won.
        """
        if self.is_tiebreaker:
            return self._score_tiebreaker(server_won)
        
        # Standard game
        self.server_points, self.receiver_points, game_won = self.scorer.score_point(
            server_won, self.server_points, self.receiver_points
        )
        return game_won

    def _score_tiebreaker(self, server_won: bool) -> bool:
        if server_won:
            self.p1_tiebreaker_points += 1
        else:
            self.p2_tiebreaker_points += 1
            
        p1 = self.p1_tiebreaker_points
        p2 = self.p2_tiebreaker_points
        
        # Tiebreaker win condition: Reach 7, margin of 2
        if (p1 >= 7 or p2 >= 7) and abs(p1 - p2) >= 2:
            return True
        return False

    def get_display_score(self) -> str:
        if self.is_tiebreaker:
            return f"{self.p1_tiebreaker_points}-{self.p2_tiebreaker_points}"
        
        s_display = self.scorer.get_display_score(self.server_points)
        r_display = self.scorer.get_display_score(self.receiver_points)
        return f"{s_display}-{r_display}"
