from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class MatchConfig:
    best_of: int = 3  # 1, 3, or 5
    games_to_win: int = 6
    tiebreaker_at: int = 6
    advantage: bool = True
    final_set_tiebreaker: bool = True

    @property
    def sets_to_win(self) -> int:
        return (self.best_of // 2) + 1
