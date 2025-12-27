import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from tennis.match import TennisMatch
from tennis.config import MatchConfig

class TestMatchFlow:
    def setup_method(self):
        self.config = MatchConfig(best_of=3, games_to_win=6, tiebreaker_at=6)
        self.match = TennisMatch("P1", "P2", self.config)

    def test_game_win_updates_score(self):
        # Win 4 points for P1
        for _ in range(4):
            self.match.point_won_by(1)
        
        assert self.match.current_set.p1_games == 1
        assert self.match.current_set.p2_games == 0

    def test_set_win(self):
        # Simulate P1 winning 6 games (assuming opponent gets 0)
        # 6 games * 4 points = 24 points
        for _ in range(24):
            self.match.point_won_by(1)
            
        assert self.match.p1_sets_won == 1
        assert self.match.current_set_index == 1 # Moved to next set
        
    def test_tiebreaker_trigger(self):
        # Manually set games to 6-6 to test trigger
        # (Bypassing point logic for setup speed, manipulating state directly for test)
        self.match.current_set.p1_games = 6
        self.match.current_set.p2_games = 6
        
        # Start new game - should be tiebreaker
        # Note: In my impl, the 'start_new_game' check happens after a game win.
        # So I need to simulate the transition from 5-6 or 6-5 to 6-6.
        
        self.match.current_set.p1_games = 5
        self.match.current_set.p2_games = 6
        self.match.current_set.start_new_game() # Normal game
        
        # Win game for P1 -> 6-6
        for _ in range(4):
            self.match.point_won_by(1)
            
        assert self.match.current_set.p1_games == 6
        assert self.match.current_set.p2_games == 6
        assert self.match.current_set.current_game.is_tiebreaker
