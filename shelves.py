import pygame
import config
from enums.cart_state import CartState
from enums.direction import Direction
from helper import obj_collision, can_interact_default, overlap
from render_game import render_text
from objects import InteractiveObject


class Shelf(InteractiveObject):
    def __init__(self, x_position, y_position, shelf_image, food_image, string_type):

        super().__init__(num_stages=1)
        self.position = [x_position, y_position]
        self.image = None
        self.food_image = None
        self.load_images(food_image, shelf_image)
        self.string_type = string_type
        self.width = 2
        self.height = 1

        self.render_offset_y = -1
        self.render_offset_x = 0

        self.food_image_file = food_image
        self.shelf_image_file = shelf_image
        self.loaded_images = False


        # self.player_inventory_limit = 12
        if shelf_image is None:
            self.is_fridge = False
        else:
            self.is_fridge = True

    def __str__(self):
        return "the {food} shelf".format(food=self.string_type)

    def load_images(self, food_image, shelf_image):
        if shelf_image is None:
            self.image = pygame.image.load("images/Shelves/shelf.png")
        else:
            self.image = shelf_image
        self.image = pygame.transform.scale(self.image, (int(2 * config.SCALE), int(2 * config.SCALE)))
        self.food_image = food_image

    def collision(self, obj, x_position, y_position):
        return overlap(self.position[0], self.position[1], self.width, self.height,
                       x_position, y_position, obj.width, obj.height)
        # return obj_collision(self, x_position, y_position, x_margin=0, y_margin=0)

    def can_interact(self, player):
        if player.direction == Direction.EAST or player.direction == Direction.WEST:
            return False
        return can_interact_default(self, player)

    def render(self, screen, camera):
        if not self.loaded_images:
            self.load_images(self.food_image_file, self.shelf_image_file)
            self.loaded_images = True

        x_position = (self.position[0] + self.render_offset_x - camera.position[0]) * config.SCALE
        y_position = (self.position[1] + self.render_offset_y - camera.position[1]) * config.SCALE
        rect = pygame.Rect(x_position, y_position, config.SCALE, config.SCALE)

        screen.blit(self.image, rect)

        # add blit for type of food-- FIX: DOESN'T ADJUST FOR CONFIG SCALE
        if self.is_fridge:
            for i in [0.9, 1.4]:
                for j in [0.2, 0.5]:
                    rect = pygame.Rect(x_position + j*config.SCALE, y_position + i*config.SCALE, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)
            for i in [0.9, 1.4]:
                for j in [1.2, 1.5]:
                    rect = pygame.Rect(x_position + j*config.SCALE, y_position + i*config.SCALE, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)

        else:
            for i in [0.9, 1.4]:
                for j in [0.3, 0.6, 0.9, 1.2, 1.5]:
                    rect = pygame.Rect(x_position + j*config.SCALE, y_position + i*config.SCALE, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)

    def interact(self, game, player):
        if player.curr_cart is None and player.curr_basket is None:
            print("here")
            if player.holding_food is not None:
                self.interaction_message = "You put " + player.holding_food + " back on the shelf."
                player.holding_food = None
                # If you put the food back in the wrong place, that violates a norm
            else:
                player.holding_food = self.string_type
                player.holding_food_image = self.food_image
                self.interaction_message = "You picked up " + self.string_type + "."
        elif player.curr_basket is None:
            self.interaction_message = "Let go of your cart to pick up food!"
        else:
            if not player.curr_basket.hit_limit():
                self.interaction_message = "You put " + self.string_type + " in your basket."
                player.curr_basket.state = CartState.FULL
                player.curr_basket.add_food(self.string_type, False)
            else:
                self.interaction_message = "The basket is full! The food won't fit."
