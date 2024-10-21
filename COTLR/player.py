from abc import ABC, abstractmethod
from enum import Enum


class Action(Enum):
    SHOOT = "shoot"
    STAB = "stab"
    LOOK = "look"
    TAKE = "take"
    RELOAD = "reload"
    DROP = "drop"
    MOVE = "move"


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Player(ABC):

    @abstractmethod
    def play(self, scores: tuple[int, int]) -> tuple[Action, Direction]:
        # use the scores so you can know when one team is scoring,
        # so you can figure out where you are vaguely if you have the flag, or vaguely where the flag is
        pass

    @abstractmethod
    def inform(self, message: str) -> None:
        pass
