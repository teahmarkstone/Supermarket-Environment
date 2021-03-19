from collections import defaultdict

import pygame
import config
from enums.direction import Direction
from enums.cart_state import CartState
from helper import obj_collision, can_interact_default, overlap
from render_game import render_text, render_textbox
from objects import InteractiveObject


class Cart(InteractiveObject):

    def hit_limit(self):
        return sum(self.contents.values()) >= self.capacity

    def interact(self, game, player):
        self.last_held = player
        if player.holding_food is not None:
            if not self.hit_limit():
                self.add_food(player.holding_food, player.bought_holding_food)
                self.interaction_message = "You put " + player.holding_food + " into your cart."
                player.take_food()
            else:
                self.interaction_message = "The cart is full! The food won't fit."
        else:
            self.interaction_message = "Just as I thought! It's a shopping cart!"

    def __str__(self):
        return "a shopping cart"

    def __init__(self, x_position, y_position, owner, direction, cart_state, capacity=12):
        super().__init__(num_stages=1)
        self.position = [x_position, y_position]
        self.owner = owner
        self.last_held = owner
        self.state = cart_state
        self.direction = direction
        self.width = .01
        self.height = .01
        self.being_held = False
        self.contents = defaultdict(int)
        self.purchased_contents = defaultdict(int)
        self.capacity = capacity
        self.set_direction(direction)

    def set_direction(self, direction):
        self.direction = direction
        if direction == Direction.NORTH or direction == Direction.SOUTH:
            self.render_offset_x = -0.25
            self.render_offset_y = -0.25
            self.width = 0.5
            self.height = 0.75
        else:
            self.render_offset_x = -0.15
            self.render_offset_y = -0.6
            self.width = 0.75
            self.height = 0.4
    
    def render(self, screen, camera):
        if self.state == CartState.EMPTY or self.state == CartState.PURCHASED:
            if self.direction == Direction.NORTH:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartEMPTYup.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.SOUTH:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartEMPTYdown.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.EAST:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartEMPTYright.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.WEST:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartEMPTYleft.png"),
                                               (config.SCALE, config.SCALE))
        elif self.state == CartState.FULL:
            if self.direction == Direction.NORTH:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartFULLup.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.SOUTH:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartFULLdown.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.EAST:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartFULLright.png"),
                                               (config.SCALE, config.SCALE))
            elif self.direction == Direction.WEST:
                image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartFULLleft.png"),
                                               (config.SCALE, config.SCALE))
        rect = pygame.Rect(
            (self.position[0] + self.render_offset_x) * config.SCALE - (camera.position[0] * config.SCALE),
            (self.position[1] + self.render_offset_y) * config.SCALE - (camera.position[1] * config.SCALE),
            config.SCALE, config.SCALE)
        screen.blit(image, rect)

    def can_interact(self, player):
        return can_interact_default(self, player)

    def empty_cart(self):
        self.contents = {}
        self.state = CartState.EMPTY

    def add_food(self, food_string, food_bought):
        if food_bought:
            self.purchased_contents[food_string] += 1
        else:
            self.contents[food_string] += 1
        self.state = CartState.FULL

    def buy(self):
        for food, quantity in self.contents.items():
            self.purchased_contents[food] += quantity
        self.contents.clear()
        # TODO - update self.owner = player, or create a new field self.buyer, or find a way to specify each item having
        # a specific buyer? The edge case is if someone buys food, then goes back into a store and has their
        # cart stolen.

    def update_position(self, x_position, y_position):
        if self.direction == Direction.NORTH:
            self.position[0] = x_position+0.05
            self.position[1] = y_position-0.85
        elif self.direction == Direction.SOUTH:
            self.position[0] = x_position+0.05
            self.position[1] = y_position+0.45
        elif self.direction == Direction.EAST:
            self.position[0] = x_position+0.65
            self.position[1] = y_position
        elif self.direction == Direction.WEST:
            self.position[0] = x_position-0.8
            self.position[1] = y_position

    def collision(self, x_position, y_position):
        return overlap(self.position[0], self.position[1], self.width, self.height,
                           x_position, y_position, 0.6, 0.4)

    def can_toggle(self, player):
        return player.direction == self.direction and can_interact_default(self, player, 0.3)