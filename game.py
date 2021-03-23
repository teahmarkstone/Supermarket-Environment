import pygame

import config
import render_game as render
from camera import Camera
from cart import Cart
from checkout import Register
from counters import Counter
from enums.direction import Direction
from enums.game_state import GameState
from enums.player_action import PlayerAction
from player import Player
from shelves import Shelf
from shoppingcarts import Carts

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

DIRECTION_TO_INT = {Direction.NORTH: 0, Direction.SOUTH: 1, Direction.EAST: 2, Direction.WEST:3}


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
    elif isinstance(obj, Shelf):
        return "shelves"
    return "misc_objects"

class Game:

    def __init__(self, screen, num_players=1, player_speed=0.07, keyboard_input=False, render_messages=False):
        self.screen = screen
        self.objects = []
        self.carts = []
        self.running = False
        self.map = []
        self.camera = Camera()

        self.game_state = GameState.NONE

        # list of all food items in game, built when shelves are made
        self.food_list = []

        # players
        self.num_players = num_players
        self.players = []
        self.curr_player = 0
        self.player_speed = player_speed

        self.keyboard_input = keyboard_input
        self.render_messages = render_messages

    def set_up(self):
        # make players
        for i in range(0, self.num_players):
            player = Player(i+1, 15, Direction.EAST, i+1)
            self.players.append(player)

        self.running = True
        self.game_state = GameState.EXPLORATORY

        self.load_map("01")

        self.set_shelves()
        self.set_registers()
        self.set_counters()
        self.set_carts()

        # randomly generates 12 item shopping list from list of food in store
        self.players[self.curr_player].set_shopping_list(self.food_list)

    # called in while running loop, handles events, renders, etc
    def update(self):
        # rendering
        self.screen.fill(config.WHITE)

        render.render_map(self.screen, self.camera, self.players[self.curr_player], self.map)
        render.render_decor(self.screen, self.camera)
        render.render_objects_and_players(self.screen, self.camera, self.objects, self.players, self.carts)
        # render.render_objects(self.screen, self.camera, self.objects)
        # render.render_players(self.screen, self.camera, self.players, self.carts)
        render.render_interactions(self, self.screen, self.objects)

        # checking keyboard input/events for either exploratory or interactive
        if self.keyboard_input:
            if self.game_state == GameState.EXPLORATORY:
                self.exploratory_events()
            elif self.game_state == GameState.INTERACTIVE:
                self.interactive_events()

        # print(self.update_observation())

    def interact(self, player_index):
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
        if self.game_state == GameState.INTERACTIVE:
            obj = self.check_interactions()
            if obj is not None:
                obj.interaction = False
                self.game_state = GameState.EXPLORATORY

    def toggle_cart(self, player_index):
        player = self.players[player_index]
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
            next_pos = [player.position[0] + speed * x1, player.position[1] + speed*y1]
            return next_pos
        except KeyError:
            return player.position

    def hits_wall(self, unit, x, y):
        wall_width = 0.4
        if unit.direction == Direction.NORTH:
            wall_width = 2
            return y <= wall_width
        if unit.direction == Direction.SOUTH:
            return y + unit.height >= len(self.map) - wall_width
        if unit.direction == Direction.EAST:
            return x + unit.width >= len(self.map[0]) - wall_width
        if unit.direction == Direction.WEST:
            return x  <= wall_width
        return False

    # TODO we may need to think a little more about the logic of breaking ties when two players move onto the same spot.
    def player_move(self, player_index, action):

        player = self.players[player_index]
        current_speed = self.player_speed  # TODO make this a property of the player

        direction, (x1, y1), anim_to_advance = ACTION_DIRECTION[action]

        if direction != player.direction:
            current_speed = 0  # The initial move just turns the player, doesn't move them.

        # If the player is holding a cart, this keeps track of whether the cart would collide with something.
        if player.curr_cart is not None:

            prev_direction = player.direction
            cart = player.curr_cart
            cart.set_direction(direction)
            cart.update_position(player.position[0] + current_speed*x1, player.position[1] + current_speed*y1)
            if self.collide(cart, cart.position[0], cart.position[1]) or self.hits_wall(cart, cart.position[0], cart.position[1]):
                # Undo the turning of the cart bc we're canceling the action
                cart.set_direction(prev_direction)
                cart.update_position(player.position[0], player.position[1])
                return

        player.direction = direction
        cart = player.curr_cart
        if cart is not None:
            cart.set_direction(direction)

        # iterating the stage the player is in, for walking animation purposes
        player.iterate_stage(anim_to_advance)
        self.move_unit(player, [current_speed * x1, current_speed * y1])
        # print(player.position)

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

    # moves player
    def move_unit(self, unit, position_change):
        new_position = [unit.position[0] + position_change[0], unit.position[1] + position_change[1]]

        if new_position[0] < 0 or new_position[0] > len(self.map[0]):
            self.running = False

        if new_position[1] < 0 or new_position[1] > len(self.map):
            self.running = False

        if self.collide(unit, new_position[0], new_position[1]):
            return

        if self.hits_wall(unit, new_position[0], new_position[1]):
            return

        unit.update_position(new_position)

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
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk.png", "milk", 5.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk.png", "milk", 7.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_chocolate.png", "chocolate milk", 9.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_chocolate.png", "chocolate milk", 11.5, 1.5)
        self.set_shelf("images/Shelves/fridge.png", "images/food/milk_strawberry.png", "strawberry milk", 13.5, 1.5)

        # fruit aisle
        self.set_shelf(None, "images/food/apples.png", "apples", 5.5, 5.5)
        self.set_shelf(None, "images/food/oranges.png", "oranges", 7.5, 5.5)
        self.set_shelf(None, "images/food/banana.png", "banana", 9.5, 5.5)
        self.set_shelf(None, "images/food/strawberry.png", "strawberry", 11.5, 5.5)
        self.set_shelf(None, "images/food/raspberry.png", "raspberry", 13.5, 5.5)

        # meat aisle
        self.set_shelf(None, "images/food/sausage.png", "sausage", 5.5, 9.5)
        self.set_shelf(None, "images/food/meat_01.png", "steak", 7.5, 9.5)
        self.set_shelf(None, "images/food/meat_02.png", "steak", 9.5, 9.5)
        self.set_shelf(None, "images/food/meat_03.png", "chicken", 11.5, 9.5)
        self.set_shelf(None, "images/food/ham.png", "ham", 13.5, 9.5)

        # cheese aisle
        self.set_shelf(None, "images/food/cheese_01.png", "brie cheese", 5.5, 13.5)
        self.set_shelf(None, "images/food/cheese_02.png", "swiss cheese", 7.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 9.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 11.5, 13.5)
        self.set_shelf(None, "images/food/cheese_03.png", "cheese wheel", 13.5, 13.5)

        # veggie aisle
        self.set_shelf(None, "images/food/garlic.png", "garlic", 5.5, 17.5)
        self.set_shelf(None, "images/food/leek_onion.png", "leek", 7.5, 17.5)
        self.set_shelf(None, "images/food/bell_pepper_red.png", "red bell pepper", 9.5, 17.5)
        self.set_shelf(None, "images/food/carrot.png", "carrot", 11.5, 17.5)
        self.set_shelf(None, "images/food/lettuce.png", "lettuce", 13.5, 17.5)

        # frozen? rn it's veggie
        self.set_shelf(None, "images/food/avocado.png", "avocado", 5.5, 21.5)
        self.set_shelf(None, "images/food/broccoli.png", "broccoli", 7.5, 21.5)
        self.set_shelf(None, "images/food/cucumber.png", "cucumber", 9.5, 21.5)
        self.set_shelf(None, "images/food/bell_pepper_yellow.png", "yellow bell pepper", 11.5, 21.5)
        self.set_shelf(None, "images/food/onion.png", "onion", 13.5, 21.5)

    # set register locations and add to object list
    def set_registers(self):
        image = pygame.transform.scale(pygame.image.load("images/Registers/registersA.png"),
                                       (int(2.3 * config.SCALE), int(3 * config.SCALE)))

        register = Register(1, 4.5, image)
        self.objects.append(register)
        image = pygame.transform.scale(pygame.image.load("images/Registers/registersB.png"),
                                       (int(2.3 * config.SCALE), int(3 * config.SCALE)))

        register = Register(1, 9.5, image)
        self.objects.append(register)

    # set counter locations and add to object list
    def set_counters(self):
        name = "prepared foods"
        image = pygame.transform.scale(pygame.image.load("images/counters/counterA.png"), (int(1.6 * config.SCALE),
                                                                                           int(3.5 * config.SCALE)))
        food_image = pygame.transform.scale(pygame.image.load("images/food/prepared.png"),
                                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        counter = Counter(18.25, 4.75, image, food_image, name)
        self.objects.append(counter)
        self.food_list.append(name)
        name = "fresh fish"
        image = pygame.transform.scale(pygame.image.load("images/counters/counterB.png"), (int(1.6 * config.SCALE),
                                                                                           int(3.5 * config.SCALE)))
        food_image = pygame.transform.scale(pygame.image.load("images/food/fresh_fish.png"),
                                            (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        counter = Counter(18.25, 10.75, image, food_image, name)
        self.objects.append(counter)
        self.food_list.append(name)

    def set_carts(self):
        shopping_carts = Carts(1, 18.5)
        self.objects.append(shopping_carts)
        shopping_carts = Carts(2, 18.5)
        self.objects.append(shopping_carts)

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

    def set_shelf(self, shelf_filename, food_filename, string_name, x_position, y_position):
        shelf_image = None
        if shelf_filename is not None:
            shelf_image = pygame.transform.scale(pygame.image.load(shelf_filename),
                                                 (int(2 * config.SCALE), int(2 * config.SCALE)))
        food = pygame.transform.scale(pygame.image.load(food_filename),
                                      (int(.30 * config.SCALE), int(.30 * config.SCALE)))
        shelf = Shelf(x_position, y_position, shelf_image, food, string_name)
        self.objects.append(shelf)
        self.food_list.append(string_name)

    def get_interactivity_data(self):
        obj = self.interaction_object(self.players[self.curr_player])
        if self.game_state == GameState.INTERACTIVE:
            return {"interactive_stage": obj.interactive_stage, "total_stages": obj.num_stages}
        else:
            return {"interactive_stage": -1, "total_stages": 0}

    def update_observation(self, render_static_objects=True):
        obs = {"players": [], "carts": []}
        obs.update(self.get_interactivity_data())

        for i, player in enumerate(self.players):
            player_data = {
                "index": player.player_number,
                "position": player.position,
                "direction": DIRECTION_TO_INT[player.direction],
                "curr_cart": self.get_cart_index(player.curr_cart),
                "shopping_list": player.shopping_list,
                "list_quant": player.list_quant,
                "holding_food": player.holding_food,
                "bought_holding_food": player.bought_holding_food
            }
            obs["players"].append(player_data)

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
                if isinstance(obj, Cart):
                    continue # We've already added all the carts.
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
        return obs

    def get_player_index(self, player):
        return index_or_minus_one(player, self.players)

    def get_cart_index(self, cart):
        return index_or_minus_one(cart, self.carts)

    # def add_player_info(self):
    #     new_player = {"index": None,
    #                   "position": [],
    #                   "direction": None,
    #                   "curr_cart": None,
    #                   "shopping_list": [],
    #                   "list_quant": [],
    #                   "holding_food": None,
    #                   "bought_holding_food": None
    #                   }
    #     supermarket_obs["player"].append(new_player)

    # def add_cart_info(self):
    #     new_cart = {"position": None,
    #                 "owner": None,
    #                 "state": None,
    #                 "direction": None,
    #                 "being_held": None,
    #                 "last_held": None,
    #                 "contents": None,
    #                 "purchased_contents": None
    #                 }
    #     supermarket_obs["cart"].append(new_cart)
