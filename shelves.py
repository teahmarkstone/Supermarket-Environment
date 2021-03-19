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

    def collision(self, x_position, y_position):
        return overlap(self.position[0], self.position[1], self.width, self.height,
                       x_position, y_position, 0.6, 0.4)
        # return obj_collision(self, x_position, y_position, x_margin=0, y_margin=0)

    def can_interact(self, player):
        if player.direction == Direction.EAST or player.direction == Direction.WEST:
            return False
        return can_interact_default(self, player)

    def render(self, screen, camera):

        x_position = (self.position[0] + self.render_offset_x - camera.position[0]) * config.SCALE
        y_position = (self.position[1] + self.render_offset_y - camera.position[1]) * config.SCALE
        rect = pygame.Rect(x_position, y_position, config.SCALE, config.SCALE)

        screen.blit(self.image, rect)

        x_position = (self.position[0] - camera.position[0]) * config.SCALE
        y_position = (self.position[1] - camera.position[1]) * config.SCALE
        rect = pygame.Rect(x_position, y_position, config.SCALE, config.SCALE)

        screen.fill((255, 0, 0), rect)

        # add blit for type of food-- FIX: DOESN'T ADJUST FOR CONFIG SCALE
        if self.is_fridge:
            for i in range(55, 100, 33):
                for j in range(13, 42, 18):
                    rect = pygame.Rect(x_position + j, y_position + i, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)
            for i in range(55, 100, 33):
                for j in range(77, 100, 18):
                    rect = pygame.Rect(x_position + j, y_position + i, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)

        else:
            for i in range(57, 100, 33):
                for j in range(19, 100, 18):
                    rect = pygame.Rect(x_position + j, y_position + i, config.SCALE, config.SCALE)
                    screen.blit(self.food_image, rect)

    def interact(self, game, player):
        if player.curr_cart is None:
            if player.holding_food is not None:
                self.interaction_message = "You put " + player.holding_food + " back on the shelf."
                player.holding_food = None
                # If you put the food back in the wrong place, that violates a norm
            else:
                player.holding_food = self.string_type
                player.holding_food_image = self.food_image
                self.interaction_message = "You picked up " + self.string_type + "."
        else:
            self.interaction_message = "Let go of your cart to pick up food!"
