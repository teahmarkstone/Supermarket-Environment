import pygame
import config
from enums.cart_state import CartState
from helper import obj_collision, overlap
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
        self.width = 2.25
        self.height = 2.5

        self.render_offset_x = 0
        self.render_offset_y = -0.5

    def __str__(self):
        return "a checkout counter"

    def collision(self, obj, x_position, y_position):
        return overlap(self.position[0], self.position[1], self.width, self.height,
                       x_position, y_position, obj.width, obj.height)

    def render(self, screen, camera):
        screen.blit(self.image, ((self.position[0] + self.render_offset_x - camera.position[0]) * config.SCALE,
                                 (self.position[1] + self.render_offset_y - camera.position[1]) * config.SCALE))

    def interact(self, game, player):
        # first interactive stage is just rendering prompt
        if not game.render_messages:
            self.interactive_stage = 1
        if self.interactive_stage == 0:
            self.interaction_message = "Hello! Would you like to check out?"
            return
        if self.interactive_stage == 1 or not game.render_messages:
            has_items = False
            x_margin = 0.5
            y_margin = 1
            if player.holding_food is not None and not player.bought_holding_food:
                player.bought_holding_food = True
                has_items = True
            for cart in game.carts:
                if cart.last_held == player \
                        and overlap(self.position[0] - x_margin, self.position[1] - y_margin, self.width + 2*x_margin,
                                    self.height + 2*y_margin, cart.position[0], cart.position[1], cart.width, cart.height):
                    if sum(cart.contents.values()) > 0:
                        cart.buy()
                        has_items = True
            if has_items:
                self.interaction_message = "Thank you for shopping with us!"
            else:
                self.interaction_message = "You need items in order to check out, silly!"
