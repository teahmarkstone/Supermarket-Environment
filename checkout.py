import config
import pygame
from collections import defaultdict
from helper import can_interact_default
from helper import overlap
from objects import InteractiveObject
from render_game import render_text


class Register(InteractiveObject):
    def can_interact(self, player):
        return can_interact_default(self, player)

    def __init__(self, x_position, y_position, image, food_directory):
        super().__init__(num_stages=2)
        self.position = [x_position, y_position]
        self.image = image
        self.width = 2.25
        self.height = 2.5

        self.render_offset_x = 0
        self.render_offset_y = -0.5
        self.food_directory = food_directory

        self.counter_capacity = 12

        self.food_images = defaultdict()
        self.food_quantities = defaultdict(int)
        self.num_items = 0
        self.prev_player = None
        self.curr_player = None

        self.checking_contents = False
        self.select_index = 0
        self.menu_length = 0
        self.selected_food = None
        self.selected_food_image = None
        self.pickup_item = False
        self.buying = False

        self.carts_in_zone = []

    def __str__(self):
        return "a checkout counter"

    def collision(self, obj, x_position, y_position):
        return overlap(self.position[0], self.position[1], self.width, self.height,
                       x_position, y_position, obj.width, obj.height)

    def render(self, screen, camera):
        screen.blit(self.image, ((self.position[0] + self.render_offset_x - camera.position[0]) * config.SCALE,
                                 (self.position[1] + self.render_offset_y - camera.position[1]) * config.SCALE))
        self.render_items(screen, camera)

    def render_items(self, screen, camera):
        x_pos = self.position[0] - camera.position[0]
        y_pos = self.position[1] - camera.position[1]

        food_positions = [[x_pos + 1.7, y_pos], [x_pos + 1.7, y_pos + .1], [x_pos + 1.7, y_pos + .2],
                          [x_pos + 1.7, y_pos + .3], [x_pos + 1.7, y_pos + .4], [x_pos + 1.7, y_pos + .5],
                          [x_pos + 1.9, y_pos + 0], [x_pos + 1.9, y_pos + .1], [x_pos + 1.9, y_pos + .2],
                          [x_pos + 1.9, y_pos + .3], [x_pos + 1.9, y_pos + .4], [x_pos + 1.9, y_pos + .5]]

        counter = 0
        for food_name in self.food_images.keys():
            for i in range(0, self.food_quantities[food_name]):
                if counter > 12:
                    counter = 0

                rect = pygame.Rect(food_positions[counter][0] * config.SCALE,
                                   food_positions[counter][1] * config.SCALE,
                                   config.SCALE, config.SCALE)
                food = pygame.transform.scale(
                    pygame.image.load(self.food_images[food_name]),
                    (int(.30 * config.SCALE), int(.30 * config.SCALE)))
                screen.blit(food, rect)
                counter += 1

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

                    if self.selected_food == "Buy":
                        self.selected_food_image = None
                        self.buying = True
                    elif self.selected_food == "Exit":
                        self.selected_food_image = None
                        self.buying = False
                    else:
                        self.buying = False
                        self.selected_food_image = pygame.transform.scale(
                            pygame.image.load(game.food_images[self.selected_food]),
                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))

    def render_contents(self, screen):

        textbox = pygame.transform.scale(pygame.image.load("text/textboxvertical.png"),
                                         (int(500), int(480)))
        select_arrow = pygame.transform.scale(pygame.image.load("text/arrow.png"), (int(20), int(20)))
        x_pos = int((config.SCREEN_WIDTH - 500) / 2)
        y_pos = int((config.SCREEN_HEIGHT - 450) / 2)
        screen.blit(textbox, (x_pos, y_pos))
        text = render_text("Checkout Menu", True, (0, 0, 0))
        screen.blit(text, (x_pos + 135, y_pos + 37))
        spacing = 30
        y_position = y_pos + 37 + spacing
        selected_food = None
        counter = 0
        for food in self.food_quantities.keys():
            if counter == self.select_index:
                selected_food = food

            # if not food in rendered_food:
            text = render_text(food, False, (0, 0, 0))

            screen.blit(text, (x_pos + 53, y_position))

            quantity = render_text(str(self.food_quantities[food]), False, (0, 0, 0))

            screen.blit(quantity, (440, y_position))
            if food == selected_food:
                screen.blit(select_arrow, (x_pos + 423, y_position - 4))
            y_position += spacing
            counter += 1

        text = render_text("Buy", True, (0, 0, 0))
        screen.blit(text, (x_pos + 53, y_position))

        text = render_text("Exit", True, (0, 0, 0))
        screen.blit(text, (x_pos + 53, y_position + spacing))


        if self.select_index == counter:
            screen.blit(select_arrow, (x_pos + 423, y_position - 4))
            selected_food = "Buy"
        elif self.select_index == counter + 1:
            screen.blit(select_arrow, (x_pos + 423, (y_position - 4) + spacing))
            selected_food = "Exit"
        self.selected_food = selected_food
        self.pickup_item = True

    def get_menu_length(self):
        return self.num_items + 1

    def interact(self, game, player):
        if game.bagging:
            if self.curr_player is None:
                self.prev_player = player
            else:
                self.prev_player = self.curr_player
            self.curr_player = player
            self.long_interact(game, player)
        else:
            self.short_interact(game, player)

    def long_interact(self, game, player):

        if self.num_items > 0 and player != self.prev_player:
            self.interaction_message = "Please wait in line."
            self.curr_player = self.prev_player
            self.interactive_stage = 1
            return
        if not game.render_messages:
            self.interactive_stage = 1
        if not player.holding_food and self.num_items == 0:
            if self.interactive_stage == 0:
                self.interaction_message = "Hello! Would you like to check out?"
                return
            if self.interactive_stage == 1:
                self.interaction_message = "Please place items on the counter."
                return
        if player.holding_food:
            if not game.render_messages:
                self.interactive_stage = 1
            if self.interactive_stage == 0:
                self.interaction_message = "Would you like to put " + player.holding_food + " on the counter?"
            if self.interactive_stage == 1:
                if self.num_items < self.counter_capacity:
                    # put food on counter
                    if player.holding_food in self.food_images:
                        self.food_quantities[player.holding_food] += 1
                    else:
                        self.food_images[player.holding_food] = game.food_images[player.holding_food]
                        self.food_quantities[player.holding_food] = 1
                    self.interaction_message = "You put " + player.holding_food + " on the counter."
                    player.holding_food = None
                    player.holding_food_image = None
                    self.num_items += 1
                else:
                    self.interaction_message = "Sorry, no more room on the counter."
            return
            # place item on counter
        if not player.holding_food and self.num_items > 0:
            if self.interactive_stage == 0:
                self.checking_contents = True
                game.item_select = True
                self.interaction_message = None
            if self.interactive_stage == 1:
                self.select_index = 0
                self.checking_contents = False
                if self.buying or not game.render_messages:
                    curr_money = self.can_afford(player, self.food_quantities)
                    if curr_money >= 0:
                        for food in self.food_quantities.keys():
                            if food in player.bagged_items:
                                player.bagged_items[food] += self.food_quantities[food]
                            else:
                                player.bagged_items[food] = self.food_quantities[food]
                        self.food_quantities.clear()
                        self.food_images.clear()
                        self.num_items = 0
                        player.budget = curr_money
                        self.interaction_message = "Thank you for shopping with us!"
                        self.buying = False
                        self.pickup_item = False
                    else:
                        self.interaction_message = "Sorry, you are short $" + str(abs(curr_money)) + "."
                        self.buying = False
                elif self.selected_food != "Exit":
                    self.pickup(self.selected_food, self.curr_player, self.selected_food_image)
                    self.pickup_item = False
                    self.interaction_message = "You took " + self.selected_food + " off the counter."
                else:
                    self.interaction_message = "Please place items on the counter."
                # buy items on counter --> give them back to player as bought items in something.. a bag? idk

    def short_interact(self, game, player):
        # first interactive stage is just rendering prompt
        if len(self.carts_in_zone) > 0 and player != self.carts_in_zone[0].last_held:
            self.interaction_message = "Please wait in line."
            self.curr_player = self.prev_player
            self.interactive_stage = 1
            return
        if not game.render_messages:
            self.interactive_stage = 1
        if self.interactive_stage == 0:
            self.interaction_message = "Hello! Would you like to check out?"
            return
        if self.interactive_stage == 1 or not game.render_messages:
            has_items = False
            can_afford = True
            curr_money = 0
            x_margin = 0.5
            y_margin = 1

            # buying food player is holding
            if player.holding_food is not None and not player.bought_holding_food:
                food_list = defaultdict(int)
                food_list[player.holding_food] = 1
                curr_money = self.can_afford(player, food_list)
                if curr_money >= 0:
                    # determine if player can afford stuff here
                    player.bought_holding_food = True
                    has_items = True
                    player.budget = curr_money
                else:
                    can_afford = False

            # buying food in carts
            for cart in game.carts:
                if cart.last_held == player \
                        and overlap(self.position[0] - x_margin, self.position[1] - y_margin, self.width + 2 * x_margin,
                                    self.height + 2 * y_margin, cart.position[0], cart.position[1], cart.width,
                                    cart.height):
                    if sum(cart.contents.values()) > 0:
                        # curr_money = self.can_afford(player, cart.contents)
                        # if curr_money >= 0:
                        # determine if player can afford stuff here
                        cart.buy()
                        has_items = True
                        # player.budget = curr_money
                        # else:
                        #    can_afford = False

            # buying food in basket
            if player.curr_basket is not None:

                if sum(player.curr_basket.contents.values()) > 0:
                    # determine if player can afford stuff here
                    curr_money = self.can_afford(player, player.curr_basket.contents)
                    if curr_money >= 0:
                        # determine if player can afford stuff here
                        player.curr_basket.buy()
                        has_items = True
                        player.budget = curr_money
                    else:
                        can_afford = False

            if has_items and can_afford:
                self.interaction_message = "Thank you for shopping with us!"
            elif can_afford:
                self.interaction_message = "You need items in order to check out, silly!"
            else:
                self.interaction_message = "Sorry, you are short $" + str(abs(curr_money)) + "."

    def can_afford(self, player, food_list):
        curr_money = player.budget
        for food in food_list:
            for i in range(0, food_list[food]):
                curr_money -= self.food_directory[food]
        return curr_money

    def pickup(self, food, player, food_image):
        # take off of counter
        self.food_quantities[food] -= 1
        player.bought_holding_food = False
        if self.food_quantities[food] == 0:
            self.food_quantities.pop(food)
            self.food_images.pop(food)


        # give to player
        player.holding_food = food
        player.holding_food_image = food_image

    def check_zones(self, game):
        x_margin = 0.5
        y_margin = 1
        for cart in game.carts:
            if overlap(self.position[0] - x_margin,
                       self.position[1] - y_margin,
                       self.width + 2 * x_margin,
                       self.height + 2 * y_margin, cart.position[0], cart.position[1],
                       cart.width,
                       cart.height):
                if cart not in self.carts_in_zone:
                    self.carts_in_zone.append(cart)
        for cart in self.carts_in_zone:
            if not overlap(self.position[0] - x_margin,
                           self.position[1] - y_margin,
                           self.width + 2 * x_margin,
                           self.height + 2 * y_margin, cart.position[0], cart.position[1],
                           cart.width,
                           cart.height):
                self.carts_in_zone.remove(cart)

