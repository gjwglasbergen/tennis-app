from typing import Optional
from tennis.match import TennisMatch
from tennis.config import MatchConfig

class MatchService:
    _instance = None
    
    def __init__(self):
        self.active_match: Optional[TennisMatch] = None
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MatchService()
        return cls._instance

    def create_match(self, p1_name: str, p2_name: str, best_of: int, games_to_win: int = 6):
        config = MatchConfig(best_of=best_of, games_to_win=games_to_win)
        self.active_match = TennisMatch(p1_name, p2_name, config)
        return self.active_match

    def get_match_state(self):
        if self.active_match:
            return self.active_match.to_json()
        return None

    def score_point(self, player_num: int):
        if self.active_match:
            self.active_match.point_won_by(player_num)
            return self.active_match.to_json()
        return None
    
    def reset_match(self):
        # Re-initialize with same names/config if needed, or just clear. 
        # For now, just clear or leave up to recreate.
        self.active_match = None
