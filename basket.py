from collections import defaultdict

import pygame

import config
from enums.cart_state import CartState
from enums.direction import Direction
from helper import can_interact_default, overlap
from objects import InteractiveObject
from render_game import render_text


class Basket(InteractiveObject):

    def hit_limit(self):
        return sum(self.contents.values()) >= self.capacity

    def interact(self, game, player):
        self.last_held = player
        if player.holding_food is not None:
            if not self.hit_limit():
                self.add_food(player.holding_food, player.bought_holding_food)
                self.interaction_message = "You put " + player.holding_food + " into your basket."
                player.take_food()
            else:
                self.interaction_message = "The basket is full! The food won't fit."
        else:
            self.checking_contents = True
            game.item_select = True
            self.interaction_message = None
        pass

    def __str__(self):
        return "a basket"

    def __init__(self, x_position, y_position, owner, direction, capacity=6):
        super().__init__(num_stages=1)
        self.position = [x_position, y_position]
        self.owner = owner
        self.last_held = owner
        self.state = CartState.EMPTY
        self.direction = direction
        self.width = 0
        self.height = 0
        self.being_held = False
        self.contents = defaultdict(int)
        self.purchased_contents = defaultdict(int)
        self.capacity = capacity
        self.set_direction(direction)
        self.render_offset_x = 0
        self.render_offset_y = 0

        self.checking_contents = False
        self.select_index = 0
        self.menu_length = 0
        self.selected_food = None
        self.selected_food_image = None
        self.pickup_item = False

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

    def render_interaction(self, game, screen):
        super().render_interaction(game, screen)
        if game.render_messages:
            self.menu_length = self.get_menu_length()
            if self.interaction is not None:
                if self.checking_contents:
                    if game.select_up:
                        game.select_up = False
                        if self.select_index != 0:
                            self.select_index -= 1

                    if game.select_down:
                        game.select_down = False
                        if self.select_index < self.menu_length:
                            self.select_index += 1
                    self.render_contents(screen)
                    if self.selected_food is not None:
                        self.selected_food_image = pygame.transform.scale(
                            pygame.image.load(game.food_images[self.selected_food]),
                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))

    def render(self, screen, camera):
        image = None
        if not self.interaction:
            self.checking_contents = False
            self.select_index = 0
            # this is messy but like whatevs
            if self.pickup_item:
                self.pickup(self.selected_food, self.last_held, self.selected_food_image)
                self.pickup_item = False
            # remove food from cart and give to player
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
        return player.curr_cart != self and can_interact_default(self, player)

    def empty_basket(self):
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

    def get_items(self):
        food_items = defaultdict(defaultdict)
        for food, quantity in self.contents.items():
            if "unpurchased" not in food_items[food]:
                food_items[food]["unpurchased"] = 0
            if "purchased" not in food_items[food]:
                food_items[food]["purchased"] = 0
            food_items[food]["unpurchased"] += quantity
        for food, quantity in self.purchased_contents.items():
            if "unpurchased" not in food_items[food]:
                food_items[food]["unpurchased"] = 0
            if "purchased" not in food_items[food]:
                food_items[food]["purchased"] = 0
            food_items[food]["purchased"] += quantity
        return food_items

    def render_contents(self, screen):

        textbox = pygame.transform.scale(pygame.image.load("text/textboxvertical.png"),
                                         (int(450), int(480)))
        select_arrow = pygame.transform.scale(pygame.image.load("text/arrow.png"), (int(20), int(20)))
        x_pos = int((config.SCREEN_WIDTH - 430) / 2)
        y_pos = int((config.SCREEN_HEIGHT - 450) / 2)
        screen.blit(textbox, (x_pos, y_pos))
        text = render_text("Item Select", True, (0, 0, 0))
        screen.blit(text, (x_pos + 120, y_pos + 37))
        spacing = 30
        y_position = y_pos + 37 + spacing
        food_items = self.get_items()
        selected_food = None
        counter = 0
        for food in food_items.keys():
            if counter == self.select_index:
                selected_food = food

            # if not food in rendered_food:
            text = render_text(food, False, (0, 0, 0))

            screen.blit(text, (x_pos + 53, y_position))

            unpurchased = render_text(str(food_items[food]["unpurchased"]), False, (250, 0, 0))
            purchased = render_text(str(food_items[food]["purchased"]), False, (0, 250, 0))

            screen.blit(unpurchased, (380, y_position))
            screen.blit(purchased, (420, y_position))
            if food == selected_food:
                screen.blit(select_arrow, (x_pos + 355, y_position - 4))
            y_position += spacing
            counter += 1

        text = render_text("Exit", True, (0, 0, 0))
        screen.blit(text, (x_pos + 53, y_position))

        if self.select_index == counter:
            screen.blit(select_arrow, (x_pos + 355, y_position - 4))
        self.selected_food = selected_food
        self.pickup_item = True

    def get_menu_length(self):
        counter = len(self.contents.items()) + len(self.purchased_contents.items())
        return counter

    def pickup(self, food, player, food_image):
        # take out of cart
        if food in self.contents:
            self.contents[food] -= 1
            player.bought_holding_food = False
            if self.contents[food] == 0:
                self.contents.pop(food)
        elif food in self.purchased_contents:
            self.purchased_contents[food] -= 1
            player.bought_holding_food = True
            if self.purchased_contents[food] == 0:
                self.purchased_contents.pop(food)

        # give to player
        player.holding_food = food
        player.holding_food_image = food_image

        # reset cart state
        if len(self.contents) == 0 and len(self.purchased_contents) == 0:
            self.state = CartState.EMPTY