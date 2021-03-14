import abc

from enums.direction import Direction
from render_game import render_textbox


class InteractiveObject(abc.ABC):
    def __init__(self, num_stages):
        self.num_stages = num_stages
        self.interaction = False
        self.interactive_stage = 0
        self.interaction_message = None
        pass

    @abc.abstractmethod
    def interact(self, game, player):
        pass

    def render_interaction(self, game, screen):
        if self.interaction and self.interaction_message is not None:
            if game.render_messages:
                render_textbox(screen, self.interaction_message)

    @abc.abstractmethod
    def can_interact(self, player):
        pass
