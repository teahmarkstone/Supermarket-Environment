import config
from collections import defaultdict
from helper import can_interact_default
from helper import overlap
from objects import InteractiveObject


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
                        and overlap(self.position[0] - x_margin, self.position[1] - y_margin, self.width + 2*x_margin,
                                    self.height + 2*y_margin, cart.position[0], cart.position[1], cart.width, cart.height):
                    if sum(cart.contents.values()) > 0:
                        #curr_money = self.can_afford(player, cart.contents)
                        #if curr_money >= 0:
                            # determine if player can afford stuff here
                        cart.buy()
                        has_items = True
                        #player.budget = curr_money
                        #else:
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

