from dataclasses import dataclass, field
from typing import List, Optional
from .config import MatchConfig
from .game import Game

@dataclass
class Set:
    config: MatchConfig
    p1_games: int = 0
    p2_games: int = 0
    history: List[str] = field(default_factory=list) # "p1", "p2"
    current_game: Optional[Game] = None
    is_completed: bool = False
    winning_player: Optional[int] = None # 1 or 2
    
    def __post_init__(self):
        if not self.current_game:
            self.start_new_game()

    def start_new_game(self, is_tiebreaker: bool = False):
        self.current_game = Game.create(self.config, is_tiebreaker=is_tiebreaker)

    def score_point(self, p1_serving: bool, p1_won_point: bool) -> bool:
        """
        Scores a point in the current game.
        Returns True if the set is won.
        """
        if self.is_completed:
            return True

        # In Game, score_point takes "server_won". 
        # So we need to map who served vs who won.
        # If p1 serving and p1 won -> server_won=True
        # If p1 serving and p2 won -> server_won=False
        # If p2 serving and p1 won -> server_won=False (receiver won)
        # If p2 serving and p2 won -> server_won=True
        
        server_won = (p1_serving and p1_won_point) or (not p1_serving and not p1_won_point)
        
        game_finished = self.current_game.score_point(server_won)
        
        if game_finished:
            # Determine game winner based on serve and game logic
            # Simpler: The Game class knows server/receiver. 
            # If server_won=True, the person serving won.
            server_won_game = server_won # Wait, score_point returns "game_won". It doesn't tell us WHO won the game directly unless we infer.
            
            # Use raw points to determine winner? Or state in Game?
            # Let's check Game state.
            winner = 0
            if self.current_game.is_tiebreaker:
                if self.current_game.p1_tiebreaker_points > self.current_game.p2_tiebreaker_points:
                    winner = 1 # Tiebreaker logic assumes p1/p2 tracking
                else:
                    winner = 2
            else:
                # Normal game
                # Ideally Game should tell us who won explicitly. 
                # Re-reading Game implementation... it returns "game_won". 
                # If server_won was passed as True/False resulting in "game_won", that means that player won.
                # So if we passed server_won=True and it returned True, Server won.
                game_winner_is_server = server_won
                
                winner = 1 if (p1_serving and game_winner_is_server) or (not p1_serving and not game_winner_is_server) else 2
            
            self._handle_game_win(winner)
            
            return self.is_completed
            
        return False

    def _handle_game_win(self, winner: int):
        if winner == 1:
            self.p1_games += 1
            self.history.append("p1")
        else:
            self.p2_games += 1
            self.history.append("p2")
            
        # Check set win conditions
        if self._check_set_won(winner):
            self.is_completed = True
            self.winning_player = winner
            self.current_game = None
        else:
            # Start next game
            # Check for tiebreaker condition
            is_tb = self._should_play_tiebreaker()
            self.start_new_game(is_tiebreaker=is_tb)

    def _check_set_won(self, last_winner: int) -> bool:
        g_win = self.config.games_to_win
        p1 = self.p1_games
        p2 = self.p2_games
        
        # Standard: 6-4 or 7-5
        if (p1 >= g_win or p2 >= g_win) and abs(p1 - p2) >= 2:
            return True
            
        # Tiebreaker won (7-6)
        if self.current_game.is_tiebreaker:
            return True
            
        return False

    def _should_play_tiebreaker(self) -> bool:
        tb_at = self.config.tiebreaker_at
        return self.p1_games == tb_at and self.p2_games == tb_at

    def get_score(self) -> str:
        return f"{self.p1_games}-{self.p2_games}"
