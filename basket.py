import random
from collections import defaultdict

import pygame

import config
from enums.cart_state import CartState
from enums.direction import Direction
from helper import can_interact_default, overlap
from objects import CartLike
from render_game import render_text


class Basket(CartLike):

    # def interact(self, game, player):
    #     self.last_held = player
    #     if player.holding_food is not None:
    #         if not self.hit_limit():
    #             self.add_food(player.holding_food, player.bought_holding_food)
    #             self.set_interaction_message(player, "You put " + player.holding_food + " into your basket.")
    #             player.take_food()
    #         else:
    #             self.set_interaction_message(player, "The basket is full! The food won't fit.")
    #     else:
    #         if not game.keyboard_input:
    #             if game.selected_food in self.contents or game.selected_food in self.purchased_contents:
    #                 self.pickup(game.selected_food, player, game.food_images[game.selected_food])
    #             game.selected_food = None
    #         self.checking_contents = True
    #         game.item_select = True
    #         self.set_interaction_message(player, None)
    #     pass

    def class_string(self):
        return "basket"

    def __str__(self):
        return "a basket"

    def __init__(self, x_position, y_position, owner, direction, capacity=6):
        super(Basket, self).__init__(x_position, y_position, owner, capacity)
        self.direction = direction
        self.width = 0
        self.height = 0
        self.set_direction(direction)
        self.render_offset_x = 0
        self.render_offset_y = 0

    def set_direction(self, direction):
        self.direction = direction
        if direction == Direction.NORTH or direction == Direction.EAST:
            self.render_offset_x = -0.25
            self.render_offset_y = -.01
            self.width = 0.15
            self.height = 0.15
        else:
            self.render_offset_x = -0.37
            self.render_offset_y = -0.25
            self.width = 0.15
            self.height = 0.15

    # def render_interaction(self, game, screen):
    #     super().render_interaction(game, screen)
    #     if game.render_messages:
    #         self.menu_length = self.get_menu_length()
    #         if self.is_interacting(game.current_player()):
    #             if self.checking_contents:
    #                 if game.keyboard_input:
    #                     if game.select_up:
    #                         game.select_up = False
    #                         if self.select_index != 0:
    #                             self.select_index -= 1
    #
    #                     if game.select_down:
    #                         game.select_down = False
    #                         if self.select_index < self.menu_length:
    #                             self.select_index += 1
    #                 self.render_contents(screen)
    #                 if self.selected_food is not None:
    #                     self.selected_food_image = pygame.transform.scale(
    #                         pygame.image.load(game.food_images[self.selected_food]),
    #                         (int(.30 * config.SCALE), int(.30 * config.SCALE)))

    def render(self, screen, camera):
        image = None
        if self.state == CartState.EMPTY or self.state == CartState.PURCHASED:
            image = pygame.transform.scale(pygame.image.load("images/baskets/grocery_basket_empty.png"),
                                               (int(.5 * config.SCALE), int(.5 * config.SCALE)))
        elif self.state == CartState.FULL:
            image = pygame.transform.scale(pygame.image.load("images/baskets/grocery_basket_full.png"),
                                               (int(.5 * config.SCALE), int(.5 * config.SCALE)))

        rect = pygame.Rect(
            (self.position[0] + self.render_offset_x) * config.SCALE - (camera.position[0] * config.SCALE),
            (self.position[1] + self.render_offset_y) * config.SCALE - (camera.position[1] * config.SCALE),
            config.SCALE, config.SCALE)
        screen.blit(image, rect)

    def can_interact(self, player):
        return player.curr_basket != self and can_interact_default(self, player)

    def update_position(self, x_position, y_position):
        if self.direction == Direction.NORTH:
            self.position[0] = x_position + 0.70
            self.position[1] = y_position
        elif self.direction == Direction.SOUTH:
            self.position[0] = x_position - 0.25
            self.position[1] = y_position + 0.23
        elif self.direction == Direction.EAST:
            self.position[0] = x_position + 0.65
            self.position[1] = y_position
        elif self.direction == Direction.WEST:
            self.position[0] = x_position - 0.20
            self.position[1] = y_position + 0.23

    def collision(self, obj, x_position, y_position):
        if not self.being_held:
            return overlap(self.position[0], self.position[1], self.width, self.height,
                        x_position, y_position, obj.width, obj.height)
        else:
            return 0

    def can_toggle(self, player):
        return can_interact_default(self, player, 0.3)