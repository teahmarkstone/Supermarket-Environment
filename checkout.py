import pygame
import config
from enums.cart_state import CartState
from helper import obj_collision
from render_game import render_text
from objects import InteractiveObject
from helper import can_interact_default


class Register(InteractiveObject):
    def can_interact(self, player):
        return can_interact_default(self, player)

    def __init__(self, x_position, y_position, image):
        super().__init__(num_stages=2)
        self.position = [x_position, y_position]
        self.image = image
        self.width = 1.5
        self.height = 2

    def collision(self, x_position, y_position):
        return obj_collision(self, x_position, y_position)

    def render(self, screen, camera):
        screen.blit(self.image, ((self.position[0] * config.SCALE) - (camera.position[0] * config.SCALE),
                                 (self.position[1] * config.SCALE) - (camera.position[1] * config.SCALE)))

    def interact(self, game, player):
        # first interactive stage is just rendering prompt
        if self.interactive_stage == 0:
            self.interaction_message = "Hello! Would you like to check out?"
            return
        if self.interactive_stage == 1:
            has_items = False
            if player.holding_food is not None and not player.bought_holding_food:
                player.bought_holding_food = True
                has_items = True
            for cart in game.carts:
                if cart.last_held == player \
                        and obj_collision(self, cart.position[0], cart.position[1], x_margin=1, y_margin=1.5):
                    if sum(cart.contents.values()) > 0:
                        cart.buy()
                        has_items = True
            if has_items:
                self.interaction_message = "Thank you for shopping with us!"
            else:
                self.interaction_message = "You need items in order to check out, silly!"
