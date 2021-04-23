from random import uniform, choice

import pygame
import config
import render_game as render
from camera import Camera
from cart import Cart
from basket import Basket
from collections import defaultdict
from checkout import Register
from counters import Counter
from enums.cart_state import CartState
from enums.direction import Direction
from enums.game_state import GameState
from enums.player_action import PlayerAction
from player import Player
from shelves import Shelf
from shoppingcarts import Carts
from baskets import Baskets

# from cart_state import CartState

ACTION_DIRECTION = {
    PlayerAction.NORTH: (Direction.NORTH, (0, -1), 0),
    PlayerAction.SOUTH: (Direction.SOUTH, (0, 1), 1),
    PlayerAction.EAST: (Direction.EAST, (1, 0), 2),
    PlayerAction.WEST: (Direction.WEST, (-1, 0), 3)
}

DIRECTION_VECTOR = {
    Direction.NORTH: (0, -1),
    Direction.SOUTH: (0, 1),
    Direction.EAST: (1, 0),
    Direction.WEST: (-1, 0)
}

DIRECTION_TO_INT = {Direction.NORTH: 0, Direction.SOUTH: 1, Direction.EAST: 2, Direction.WEST: 3}
DIRECTIONS = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

# milk aisle
FOOD_IMAGES = {
    "milk": "images/food/milk.png",
    "chocolate milk": "images/food/milk_chocolate.png",
    "strawberry milk": "images/food/milk_strawberry.png",

    # fruit aisle
    "apples": "images/food/apples.png",
    "oranges": "images/food/oranges.png",
    "banana": "images/food/banana.png",
    "strawberry": "images/food/strawberry.png",
    "raspberry": "images/food/raspberry.png",

    # meat aisle
    "sausage": "images/food/sausage.png",
    "steak": "images/food/meat_01.png",
    "chicken": "images/food/meat_03.png",
    "ham": "images/food/ham.png",

    # cheese aisle
    "brie cheese": "images/food/cheese_01.png",
    "swiss cheese": "images/food/cheese_02.png",
    "cheese wheel": "images/food/cheese_03.png",

    # veggie aisle
    "garlic": "images/food/garlic.png",
    "leek": "images/food/leek_onion.png",
    "red bell pepper": "images/food/bell_pepper_red.png",
    "carrot": "images/food/carrot.png",
    "lettuce": "images/food/lettuce.png",

    # frozen? rn it's veggie
    "avocado": "images/food/avocado.png",
    "broccoli": "images/food/broccoli.png",
    "cucumber": "images/food/cucumber.png",
    "yellow bell pepper": "images/food/bell_pepper_yellow.png",
    "onion": "images/food/onion.png"
}

def index_or_minus_one(item, the_list):
    if item is None:
        return -1
    try:
        return the_list.index(item)
    except ValueError:
        return -1


def get_obj_category(obj):
    if isinstance(obj, Register):
        return "registers"
    elif isinstance(obj, Counter):
        return "counters"
    elif isinstance(obj, Carts):
        return "cartReturns"
    elif isinstance(obj, Baskets):
        return "basketReturns"
    elif isinstance(obj, Shelf):
        return "shelves"
    return "misc_objects"


class Game:

    def __init__(self, num_players=1, player_speed=0.07, keyboard_input=False, render_messages=False,
                 headless=False, initial_state_filename=None, follow_player=-1, random_start=False):

        self.screen = None
        self.clock = None

        if not headless:
            if follow_player == -1:
                config.SCALE = 32
                config.SCREEN_HEIGHT = 800
                config.SCREEN_WIDTH = 640
            pygame.init()
            pygame.display.set_caption("Supermarket Environment")
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            self.clock = pygame.time.Clock()

        self.objects = []
        self.carts = []
        self.baskets = []
        self.running = False
        self.map = []
        self.camera = Camera()
        self.food_directory = defaultdict(int)

        self.num_players = num_players
        self.game_state = GameState.NONE
        self.players = []

        if initial_state_filename is not None:
            self.load_from_file(initial_state_filename)

        # list of all food items in game, built when shelves are made
        self.food_list = []

        # players

        self.player_speed = player_speed

        self.curr_player = follow_player

        self.keyboard_input = keyboard_input
        self.render_messages = render_messages
        self.headless = headless
        self.random_start = random_start

    def set_observation(self, obs):
        self.players = []
        self.carts = []
        self.baskets = []
        for player_dict in obs['players']:
            pos = player_dict['position']
            player = Player(pos[0], pos[1], DIRECTIONS[player_dict['direction']], player_dict['index'])
            player.shopping_list = player_dict['shopping_list']
            player.list_quant = player_dict['list_quant']
            player.holding_food = player_dict['holding_food']
            player.budget = player_dict['budget']
            if player.holding_food is not None:
                player.holding_food_image = FOOD_IMAGES[player.holding_food]
            player.bought_holding_food = player_dict['bought_holding_food']
            self.players.append(player)

            basket_dict = obs['baskets']
            pos = basket_dict['position']
            basket = Basket(pos[0], pos[1], player, DIRECTIONS[basket_dict["direction"]], basket_dict["capacity"])
            if sum(basket_dict["contents_quant"]) + sum(basket_dict["purchased_quant"]) > 0:
                basket.state = CartState.FULL
            for i, string in enumerate(basket_dict["contents"]):
                basket.contents[string] = basket_dict["contents_quant"]
            for i, string in enumerate(basket_dict["purchased_contents"]):
                basket.purchased_contents[string] = basket_dict["purchased_quant"]
            self.objects.append(basket)

        for cart_dict in obs['carts']:
            pos = cart_dict['position']
            cart = Cart(pos[0], pos[1], self.players[cart_dict["owner"]], DIRECTIONS[cart_dict["direction"]],
                        cart_dict["capacity"])
            last_held = cart_dict["last_held"]
            cart.last_held = self.players[last_held] if last_held != -1 else None
            if sum(cart_dict["contents_quant"]) + sum(cart_dict["purchased_quant"]) > 0:
                cart.state = CartState.FULL
            for i, string in enumerate(cart_dict["contents"]):
                cart.contents[string] = cart_dict["contents_quant"]
            for i, string in enumerate(cart_dict["purchased_contents"]):
                cart.purchased_contents[string] = cart_dict["purchased_quant"]
            self.carts.append(cart)
            self.objects.append(cart)

        for i, player in enumerate(self.players):
            cart_num = obs['players'][i]["curr_cart"]
            player.curr_cart = self.carts[cart_num] if cart_num != -1 else None

        self.num_players = len(self.players)

    def load_from_file(self, file_path):
        from ast import literal_eval
        with open(file_path, "r") as file:
            contents = file.read()
            obs = literal_eval(contents)
            self.set_observation(obs)

    def set_up(self):

        self.running = True
        self.game_state = GameState.EXPLORATORY

        self.load_map("01")

        self.set_shelves()
        self.set_counters()
        self.set_registers()
        self.set_carts()
        self.set_baskets()
        # make players

        if len(self.players) == 0:
            for i in range(0, self.num_players):
                player = Player(i + 1.2, 15.6, Direction.EAST, i + 1)
                if self.random_start:
                    self.randomize_position(player)
                player.set_shopping_list(self.food_list)
                self.players.append(player)  # randomly generates 12 item shopping list from list of food in store

    def randomize_position(self, player):
        player.direction = choice(DIRECTIONS)
        x = 0
        y = 0
        while self.collide(player, x, y) or self.hits_wall(player, x, y):
            x = uniform(0, 20)
            y = uniform(0, 25)
        player.position = [x, y]

    def save_state(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.observation(False)))

    # called in while running loop, handles events, renders, etc
    def update(self):
        # rendering
        if not self.headless:
            self.clock.tick(120)
            if not self.running:
                pygame.quit()
                return

            if self.keyboard_input:
                pass
                # if self.game_state == GameState.EXPLORATORY:
                #     self.exploratory_events()
                # elif self.game_state == GameState.INTERACTIVE:
                #     self.interactive_events()
            else:
                pygame.event.pump()

            self.screen.fill(config.WHITE)

            render.render_map(self.screen, self.camera,
                              self.players[self.curr_player] if self.curr_player >= 0 else None,
                              self.map)
            render.render_decor(self.screen, self.camera)
            render.render_objects_and_players(self.screen, self.camera, self.objects, self.players, self.carts,
                                              self.baskets)
            render.render_interactions(self, self.screen, self.objects)

            if self.render_messages:
                render.render_money(self.screen, self.camera, self.players[self.curr_player])
            # checking keyboard input/events for either exploratory or interactive
            pygame.display.flip()

    def interact(self, player_index):
        if self.players[player_index].left_store:
            return
        if self.game_state == GameState.EXPLORATORY:
            player = self.players[player_index]
            obj = self.interaction_object(player)
            if obj is not None:
                obj.interaction = True
                obj.interact(self, player)
                if self.render_messages:
                    self.game_state = GameState.INTERACTIVE
        elif self.game_state == GameState.INTERACTIVE:
            obj = self.check_interactions()
            if obj is not None:
                # if number of completed stages exceeds the number of stages for the object, end interaction
                if obj.interactive_stage + 1 >= obj.num_stages:
                    obj.interactive_stage = 0
                    # this is what turns off rendering of text screens
                    obj.interaction = False
                    self.game_state = GameState.EXPLORATORY
                else:
                    # continue interaction
                    obj.interactive_stage += 1
                    obj.interact(self, self.players[player_index])

    def cancel_interaction(self, i):
        if self.players[i].left_store:
            return
        if self.game_state == GameState.INTERACTIVE:
            obj = self.check_interactions()
            if obj is not None:
                obj.interaction = False
                self.game_state = GameState.EXPLORATORY

    def toggle_cart(self, player_index):
        player = self.players[player_index]
        if player.left_store:
            return
        if player.curr_cart is not None:
            player.curr_cart.being_held = False
            player.curr_cart = None
        else:
            # Player can't pick up the cart if they're holding food
            if player.holding_food is None:
                # check if player is holding onto cart (should prob restructure bc this is ugly)
                for cart in self.carts:
                    if cart.can_toggle(player) and not cart.being_held:
                        # Ensure you can't pick up a cart someone else is currently holding
                        player.curr_cart = cart
                        cart.last_held = player
                        cart.being_held = True
                        break

    # TODO: not working currently, not sure if player should be able to put basket down
    def toggle_basket(self, player_index):
        player = self.players[player_index]
        if player.left_store:
            return
        if player.curr_basket is not None:
            player.curr_basket.being_held = False
            player.curr_basket = None
        else:
            # Player can't pick up the cart if they're holding food
            if player.holding_food is None:
                # check if player is holding onto cart (should prob restructure bc this is ugly)
                for basket in self.baskets:
                    if basket.can_toggle(player) and not basket.being_held:
                        # Ensure you can't pick up a cart someone else is currently holding
                        player.curr_basket = basket
                        basket.last_held = player
                        basket.being_held = True
                        break

    def nop(self, player):
        self.players[player].stand_still()

    def next_direction(self, player, action):
        try:
            direction, (x1, y1), anim_to_advance = ACTION_DIRECTION[action]
            return direction
        except KeyError:
            return player.direction

    def next_position(self, player, action):
        try:
            direction, (x1, y1), anim_to_advance = ACTION_DIRECTION[action]
            speed = self.player_speed if player.direction == direction else 0.
            next_pos = [player.position[0] + speed * x1, player.position[1] + speed * y1]
            return next_pos
        except KeyError:
            return player.position

    def at_door(self, unit, x, y):
        return (x >= 0 and self.map[round(y - 0.4)][round(x)] == "F") or (x <= 0 and self.map[round(y - 0.4)][round(x+unit.width)] == "F")

    def hits_wall(self, unit, x, y):
        wall_width = 0.4
        return y <= 2 or y + unit.height >= len(self.map) - wall_width or \
               x + unit.width >= len(self.map[0]) - wall_width or (x <= wall_width and
                                                                   not self.at_door(unit, x, y))

    # TODO we may need to think a little more about the logic of breaking ties when two players move onto the same spot.
    def player_move(self, player_index, action):

        player = self.players[player_index]
        if player.left_store:
            return

        current_speed = self.player_speed  # TODO make this a property of the player

        direction, (x1, y1), anim_to_advance = ACTION_DIRECTION[action]

        if direction != player.direction:
            current_speed = 0  # The initial move just turns the player, doesn't move them.
        else:
            # iterating the stage the player is in, for walking animation purposes
            player.iterate_stage(anim_to_advance)

        # If the player is holding a cart, this keeps track of whether the cart would collide with something.
        if player.curr_cart is not None:
            prev_direction = player.direction
            cart = player.curr_cart
            cart.set_direction(direction)
            cart.update_position(player.position[0] + current_speed * x1, player.position[1] + current_speed * y1)
            if self.collide(cart, cart.position[0], cart.position[1]) or self.hits_wall(cart, cart.position[0],
                                                                                        cart.position[1]):
                # Undo the turning of the cart bc we're canceling the action
                cart.set_direction(prev_direction)
                cart.update_position(player.position[0], player.position[1])
                return

        player.direction = direction
        cart = player.curr_cart
        if cart is not None:
            cart.set_direction(direction)
        basket = player.curr_basket
        if basket is not None:
            basket.set_direction(direction)

        self.move_unit(player, [current_speed * x1, current_speed * y1])


    # main keyboard input
    def exploratory_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    self.interact(self.curr_player)

                # i key shows inventory
                elif event.key == pygame.K_i:
                    self.players[self.curr_player].render_shopping_list = False
                    self.players[self.curr_player].render_inventory = True
                    self.game_state = GameState.INTERACTIVE

                # l key shows shopping list
                elif event.key == pygame.K_l:
                    self.players[self.curr_player].render_inventory = False
                    self.players[self.curr_player].render_shopping_list = True
                    self.game_state = GameState.INTERACTIVE

                # switch players
                elif event.key == pygame.K_1:
                    self.curr_player = 0
                elif event.key == pygame.K_2:
                    self.curr_player = 1

                elif event.key == pygame.K_c:
                    self.toggle_cart(self.curr_player)
                # elif event.key == pygame.K_b:
                #     self.toggle_basket(self.curr_player)

            # player stands still if not moving, player stops holding cart if c button released
            if event.type == pygame.KEYUP:
                self.nop(self.curr_player)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:  # up
            self.player_move(self.curr_player, PlayerAction.NORTH)

        elif keys[pygame.K_DOWN]:  # down
            self.player_move(self.curr_player, PlayerAction.SOUTH)

        elif keys[pygame.K_LEFT]:  # left
            self.player_move(self.curr_player, PlayerAction.WEST)

        elif keys[pygame.K_RIGHT]:  # right
            self.player_move(self.curr_player, PlayerAction.EAST)

    # keyboard input when player is interacting with an object
    def interactive_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # b key cancels interaction
                elif event.key == pygame.K_b:
                    self.cancel_interaction(self.curr_player)

                # return key continues interaction
                elif event.key == pygame.K_RETURN:
                    self.interact(self.curr_player)
                # i key turns off inventory rendering
                elif event.key == pygame.K_i:
                    if self.players[self.curr_player].render_inventory:
                        self.players[self.curr_player].render_inventory = False
                        self.game_state = GameState.EXPLORATORY
                # l key turns off shopping list rendering
                elif event.key == pygame.K_l:
                    if self.players[self.curr_player].render_shopping_list:
                        self.players[self.curr_player].render_shopping_list = False
                        self.game_state = GameState.EXPLORATORY

    # Reading in map
    def load_map(self, file_name):
        with open("maps/" + file_name + ".txt") as map_file:
            for line in map_file:
                tiles = []
                for i in range(0, len(line) - 1, 2):
                    tiles.append(line[i])
                self.map.append(tiles)

    def out_of_bounds(self, player):
        return player.position[0] < 0 or player.position[0] > len(self.map[0]) \
               or player.position[1] < 0 or player.position[1] > len(self.map)

    # moves player
    def move_unit(self, unit, position_change):
        new_position = [unit.position[0] + position_change[0], unit.position[1] + position_change[1]]

        if self.collide(unit, new_position[0], new_position[1]):
            return

        if self.hits_wall(unit, new_position[0], new_position[1]):
            return

        # TODO stop rendering and disable actions for players who have left the store.

        unit.update_position(new_position)
        if self.out_of_bounds(unit):
            unit.left_store = True

        if all(self.out_of_bounds(player) for player in self.players) or \
            (self.curr_player >= 0 and self.out_of_bounds(self.players[self.curr_player])):
            self.running = False

    # checks if given [x,y] collides with an object
    def collide(self, unit, x_position, y_position):
        for object in self.objects:
            if isinstance(unit, Player) and unit.curr_cart is not None and object == unit.curr_cart:
                continue
            elif unit == object:
                continue
            if object.collision(unit, x_position, y_position):
                return True
        # checking if players are colliding
        for player in self.players:
            if player != unit:
                if player.collision(unit, x_position, y_position):
                    return True
        return False

    # set shelf locations and add to object list
    def set_shelves(self):

        # milk aisle
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk.png", "milk", 2, 5.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk.png", "milk", 2, 7.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_chocolate.png", "chocolate milk", 2, 9.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_chocolate.png", "chocolate milk", 2, 11.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_strawberry.png", "strawberry milk", 2, 13.5, 1.5)


        # fruit aisle
        self.set_shelf(None, "images/food/apples.png", "apples", 5, 5.5, 5.5)
        self.set_shelf(None, "images/food/oranges.png", "oranges", 5, 7.5, 5.5)
        self.set_shelf(None, "images/food/banana.png", "banana", 1, 9.5, 5.5)
        self.set_shelf(None, "images/food/strawberry.png", "strawberry", 1, 11.5, 5.5)
        self.set_shelf(None, "images/food/raspberry.png", "raspberry", 1, 13.5, 5.5)

        # meat aisle
        self.set_shelf(None, "images/food/sausage.png", "sausage", 4, 5.5, 9.5)
        self.set_shelf(None, "images/food/meat_01.png", "steak", 5, 7.5, 9.5)
        self.set_shelf(None, "images/food/meat_02.png", "steak", 5, 9.5, 9.5)
        self.set_shelf(None, "images/food/meat_03.png", "chicken", 6, 11.5, 9.5)
        self.set_shelf(None, "images/food/ham.png", "ham", 6, 13.5, 9.5)

        # cheese aisle
        self.set_shelf(None, "images/food/cheese_01.png", "brie cheese", 5, 5.5, 13.5)
        self.set_shelf(None, "images/food/cheese_02.png", "swiss cheese", 5, 7.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 15, 9.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 15, 11.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 15, 13.5, 13.5)

        # veggie aisle
        self.set_shelf(None, "images/food/garlic.png", "garlic", 2, 5.5, 17.5)
        self.set_shelf(None, "images/food/leek_onion.png", "leek", 1, 7.5, 17.5)
        self.set_shelf(None, "images/food/bell_pepper_red.png", "red bell pepper", 2, 9.5, 17.5)
        self.set_shelf(None, "images/food/carrot.png", "carrot", 1, 11.5, 17.5)
        self.set_shelf(None, "images/food/lettuce.png", "lettuce", 2, 13.5, 17.5)

        # frozen? rn it's veggie
        self.set_shelf(None, "images/food/avocado.png", "avocado", 2, 5.5, 21.5)
        self.set_shelf(None, "images/food/broccoli.png", "broccoli", 1, 7.5, 21.5)
        self.set_shelf(None, "images/food/cucumber.png", "cucumber", 2, 9.5, 21.5)
        self.set_shelf(None, "images/food/bell_pepper_yellow.png", "yellow bell pepper", 2, 11.5, 21.5)
        self.set_shelf(None, "images/food/onion.png", "onion", 2, 13.5, 21.5)

    # set register locations and add to object list
    def set_registers(self):
        if not self.headless:
            image = pygame.transform.scale(pygame.image.load("images/Registers/registersA.png"),
                                       (int(2.3 * config.SCALE), int(3 * config.SCALE)))
        else:
            image = None
        register = Register(1, 4.5, image, self.food_directory)
        self.objects.append(register)
        if not self.headless:
            image = pygame.transform.scale(pygame.image.load("images/Registers/registersB.png"),
                                       (int(2.3 * config.SCALE), int(3 * config.SCALE)))
        else:
            image = None
        register = Register(1, 9.5, image, self.food_directory)
        self.objects.append(register)

    # set counter locations and add to object list
    def set_counters(self):
        name = "prepared foods"
        if not self.headless:
            image = pygame.transform.scale(pygame.image.load("images/counters/counterA.png"), (int(1.6 * config.SCALE),
                                                                                           int(3.5 * config.SCALE)))
            food_image = pygame.transform.scale(pygame.image.load("images/food/prepared.png"),
                                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        else:
            image = None
            food_image = None
        counter = Counter(18.25, 4.75, image, food_image, name)
        self.objects.append(counter)
        self.food_list.append(name)
        self.food_directory[name] = 15
        name = "fresh fish"
        if not self.headless:
            image = pygame.transform.scale(pygame.image.load("images/counters/counterB.png"), (int(1.6 * config.SCALE),
                                                                                           int(3.5 * config.SCALE)))
            food_image = pygame.transform.scale(pygame.image.load("images/food/fresh_fish.png"),
                                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        else:
            image = None
            food_image = None
        counter = Counter(18.25, 10.75, image, food_image, name)
        self.objects.append(counter)
        name = "fresh fish"
        if not self.headless:
            image = pygame.transform.scale(pygame.image.load("images/counters/counterB.png"), (int(1.6 * config.SCALE),
                                                                                           int(3.5 * config.SCALE)))
            food_image = pygame.transform.scale(pygame.image.load("images/food/fresh_fish.png"),
                                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        else:
            image = None
            food_image = None
        counter = Counter(18.25, 10.75, image, food_image, name)
        self.objects.append(counter)
        self.food_list.append(name)
        self.food_list.append(name)
        self.food_directory[name] = 15

    def set_carts(self):
        shopping_carts = Carts(1, 18.5)
        self.objects.append(shopping_carts)
        shopping_carts = Carts(2, 18.5)
        self.objects.append(shopping_carts)

    def set_baskets(self):
        baskets = Baskets(3.5, 18.5)
        self.objects.append(baskets)

    # checking if a player is facing an object
    # TODO maybe alter so that shopping carts have slightly different interaction zones?
    def interaction_object(self, player):
        for obj in self.objects:
            if obj.can_interact(player):
                return obj
        return None

    # checks if any objects are being interacted with
    def check_interactions(self):
        for object in self.objects:
            if object.interaction:
                return object

        return None

    def set_shelf(self, shelf_filename, food_filename, string_name, food_price, x_position, y_position):
        quantity = 20
        shelf_image = None
        food = None
        if not self.headless:
            if shelf_filename is not None:
                shelf_image = pygame.transform.scale(pygame.image.load(shelf_filename),
                                                 (int(2 * config.SCALE), int(2 * config.SCALE)))
            food = pygame.transform.scale(pygame.image.load(food_filename),
                                      (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        shelf = Shelf(x_position, y_position, shelf_image, food, string_name, food_price, quantity)
        self.food_directory[string_name] = food_price
        self.objects.append(shelf)
        self.food_list.append(string_name)

    def get_interactivity_data(self):
        obj = self.interaction_object(self.players[self.curr_player])
        if self.game_state == GameState.INTERACTIVE and obj is not None:
            return {"interactive_stage": obj.interactive_stage, "total_stages": obj.num_stages}
        else:
            return {"interactive_stage": -1, "total_stages": 0}

    def observation(self, render_static_objects=True):
        obs = {"players": [], "carts": [], "baskets": []}
        obs.update(self.get_interactivity_data())

        for i, player in enumerate(self.players):
            player_data = {
                "index": player.player_number,
                "position": player.position,
                "width": player.width,
                "height": player.height,
                "direction": DIRECTION_TO_INT[player.direction],
                "curr_cart": self.get_cart_index(player.curr_cart),
                "shopping_list": player.shopping_list,
                "list_quant": player.list_quant,
                "holding_food": player.holding_food,
                "bought_holding_food": player.bought_holding_food,
                "budget": player.budget,
            }
            obs["players"].append(player_data)

            basket = player.curr_basket
            if basket is not None:
                basket_data = {
                    "position": basket.position,
                    "direction": DIRECTION_TO_INT[basket.direction],
                    "capacity": basket.capacity,
                    "owner": self.get_player_index(basket.owner),
                    "last_held": self.get_player_index(basket.last_held),
                    "contents": [food for food in basket.contents],
                    "contents_quant": [basket.contents[food] for food in basket.contents],
                    "purchased_contents": [food for food in basket.purchased_contents],
                    "purchased_quant": [basket.purchased_contents[food] for food in basket.purchased_contents],
                    "width": basket.width,
                    "height": basket.height,
                }
                obs["baskets"].append(basket_data)

        for i, cart in enumerate(self.carts):
            cart_data = {
                "position": cart.position,
                "direction": DIRECTION_TO_INT[cart.direction],
                "capacity": cart.capacity,
                "owner": self.get_player_index(cart.owner),
                "last_held": self.get_player_index(cart.last_held),
                "contents": [food for food in cart.contents],
                "contents_quant": [cart.contents[food] for food in cart.contents],
                "purchased_contents": [food for food in cart.purchased_contents],
                "purchased_quant": [cart.purchased_contents[food] for food in cart.purchased_contents],
                "width": cart.width,
                "height": cart.height,
            }
            obs["carts"].append(cart_data)

        if render_static_objects:
            for obj in self.objects:
                if isinstance(obj, Cart) or isinstance(obj, Basket):
                    continue  # We've already added all the carts and baskets.
                object_data = {
                    "height": obj.height,
                    "width": obj.width,
                    "position": obj.position,
                }
                if isinstance(obj, Shelf) or isinstance(obj, Counter):
                    object_data["food"] = obj.string_type
                category = get_obj_category(obj)
                if category not in obs:
                    obs[category] = []
                obs[category].append(object_data)

        # TODO: not sure if this is the right way to do this
        obs["food_prices"] = self.food_directory
        return obs

    def get_player_index(self, player):
        return index_or_minus_one(player, self.players)

    def get_cart_index(self, cart):
        return index_or_minus_one(cart, self.carts)

