import pygame
import config
from enums.cart_state import CartState
from cart import Cart
from enums.direction import Direction
from helper import obj_collision, can_interact_default
from render_game import render_text
from objects import InteractiveObject


class Carts(InteractiveObject):
    def __init__(self, x_position, y_position):
        super().__init__(num_stages=1)
        self.position = [x_position, y_position]
        self.width = 0.1
        self.height = 5

        self.image = pygame.transform.scale(pygame.image.load("images/cart/shoppingcartrack.png"),
                                            (int(1.5 * config.SCALE),
                                             6 * config.SCALE))

    def __str__(self):
        return "the cart return"

    def render(self, screen, camera):
        screen.blit(self.image, ((self.position[0] * config.SCALE) - (camera.position[0] * config.SCALE),
                                 (self.position[1] * config.SCALE) - (camera.position[1] * config.SCALE)))

    def can_interact(self, player):
        if player.direction == Direction.SOUTH:
            return can_interact_default(self, player)
        return False

    def collision(self, x_position, y_position):
        return obj_collision(self, x_position, y_position, x_margin=0.7)

    def interact(self, game, player):
        if self.interactive_stage == 0:
            # Player is not holding a cart
            if player.curr_cart is None:
                if player.holding_food is None:
                    new_cart = Cart(player.position[0],
                                    player.position[1],
                                    player,
                                    Direction.SOUTH,
                                    CartState.EMPTY)
                    game.carts.append(new_cart)
                    game.objects.append(new_cart)
                    player.curr_cart = new_cart
                    new_cart.being_held = True
                    self.interaction_message = "You picked up shopping cart. Press c to let go and pick up."
                else:
                    self.interaction_message = "Can't pick up a cart while holding food!"
                # Player is holding a cart; return it
            else:
                self.interaction_message = "You put the shopping cart back."
                cart = player.curr_cart
                player.curr_cart = None
                game.carts.remove(cart)
                game.objects.remove(cart)
