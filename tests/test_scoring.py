import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from tennis.scoring.point_scorer import AdvantagePointScorer, NoAdvantagePointScorer

class TestAdvantageScoring:
    def setup_method(self):
        self.scorer = AdvantagePointScorer()

    def test_basic_scoring(self):
        # 0-0 -> 15-0
        s, r, w = self.scorer.score_point(True, 0, 0)
        assert s == 1 # 15
        assert r == 0
        assert not w

        # 30-30 -> 40-30
        s, r, w = self.scorer.score_point(True, 2, 2)
        assert s == 3 # 40
        assert r == 2 # 30
        assert not w

    def test_deuce_logic(self):
        # 40-40 (Deuce) -> AD-40
        s, r, w = self.scorer.score_point(True, 3, 3)
        assert s == 4 # AD
        assert r == 3 # 40
        assert not w
        
        # AD-40 -> Game
        s, r, w = self.scorer.score_point(True, 4, 3)
        assert s == 5
        assert w

        # AD-40 -> Deuce (Back to 3-3)
        # Specific logic: If server has AD (4) and loses, both go back to 3 (Deuce)? 
        # Or does receiver go to 4?
        # In my impl: if loser has 4 (AD), we return (3,3).
        s, r, w = self.scorer.score_point(False, 4, 3) # Server has AD, Server Loses
        assert s == 3
        assert r == 3
        assert not w

class TestNoAdvantageScoring:
    def setup_method(self):
        self.scorer = NoAdvantagePointScorer()

    def test_sudden_death(self):
        # 40-40 -> Game
        s, r, w = self.scorer.score_point(True, 3, 3)
        assert s == 4
        assert w
