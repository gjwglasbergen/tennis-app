from abc import ABC, abstractmethod
from typing import Tuple, Literal, Optional

PointValue = Literal[0, 15, 30, 40, "AD"]


class PointScorer(ABC):
    @abstractmethod
    @abstractmethod
    def score_point(self, server_won: bool, server_points: int, receiver_points: int) -> Tuple[int, int, bool]:
        """
        Calculates the new score after a point is won by the server or receiver.
        
        Args:
            server_points: Current points of the server (0=0, 1=15, 2=30, 3=40)
            receiver_points: Current points of the receiver
            
        Returns:
            Tuple of (new_server_points, new_receiver_points, game_won)
        """
        pass
    
    @abstractmethod
    def get_display_score(self, points: int) -> PointValue:
        pass


class StandardPointScorer(PointScorer):
    """Base class for standard scoring logic."""
    
    POINT_MAP = {0: 0, 1: 15, 2: 30, 3: 40}

    def get_display_score(self, points: int) -> PointValue:
        return self.POINT_MAP.get(points, 0) # Fallback, though typically shouldn't happen beyond 3 without game end or deuce handling logic override


class NoAdvantagePointScorer(StandardPointScorer):
    def score_point(self, server_won: bool, p1_points: int, p2_points: int) -> Tuple[int, int, bool]:
        # p1 is technical "player who won point", p2 is "opponent"
        # Wait, the interface should probably be generally "server/receiver" or just "p1/p2" state
        # Let's simplify: inputs are abstract points (0,1,2,3).
        
        if server_won:
            if p1_points == 3:
                return 4, p2_points, True # Game won
            return p1_points + 1, p2_points, False
        else:
            if p2_points == 3:
                return p1_points, 4, True
            return p1_points, p2_points + 1, False


class AdvantagePointScorer(StandardPointScorer):
    def get_display_score(self, points: int) -> PointValue:
        if points == 4:
            return "AD"
        return super().get_display_score(points)

    def score_point(self, server_won: bool, p1_points: int, p2_points: int) -> Tuple[int, int, bool]:
        """
        Score a point. 
        Args:
            p1_win: True if player 1 (first arg points) won the point.
            p1_points: Player 1's current raw points (0,1,2,3,4=AD)
            p2_points: Player 2's current raw points
        """
        winner_points = p1_points if server_won else p2_points
        loser_points = p2_points if server_won else p1_points
        
        if winner_points <= 2:
            # 0->15, 15->30, 30->40
            return (p1_points + 1, p2_points, False) if server_won else (p1_points, p2_points + 1, False)
            
        if winner_points == 3:
            # 40 situations
            if loser_points < 3:
                # 40-0, 40-15, 40-30 -> Game
                return (4, p2_points, True) if server_won else (p1_points, 4, True)
            elif loser_points == 3:
                # Deuce -> AD
                return (4, 3, False) if server_won else (3, 4, False)
            elif loser_points == 4:
                # Opponent has AD -> Back to Deuce (3-3)
                return (3, 3, False)
                
        if winner_points == 4:
            # AD -> Game
            return (5, p2_points, True) if server_won else (p1_points, 5, True)
            
        # Should not happen in normal flow
        return (p1_points, p2_points, False)

def create_point_scorer(advantage: bool) -> PointScorer:
    return AdvantagePointScorer() if advantage else NoAdvantagePointScorer()
