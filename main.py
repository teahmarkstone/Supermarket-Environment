import pygame
import config
from enums.game_state import GameState
from enums.player_action import PlayerAction
from env import SupermarketEnv
from game import Game
from norms.theft import CartTheftNorm


class SupermarketEventHandler:
    def __init__(self, env):
        self.curr_player = 0
        self.env = env
        env.reset()
        self.running = True

    def single_player_action(self, action):
        full_action = [PlayerAction.NOP]*self.env.num_players
        full_action[self.curr_player] = action
        return full_action

    def handle_events(self):
        if self.env.game.game_state == GameState.EXPLORATORY:
            self.handle_exploratory_events()
        else:
            self.handle_interactive_events()

    def handle_exploratory_events(self):
        # print("DID THIS")
        # print(self.env.game.update_observation())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.env.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.env.game.running = False
                elif event.key == pygame.K_RETURN:
                    self.env.step(self.single_player_action(PlayerAction.INTERACT))
                # i key shows inventory
                elif event.key == pygame.K_i:
                    self.env.game.players[self.curr_player].render_shopping_list = False
                    self.env.game.players[self.curr_player].render_inventory = True
                    self.env.game.game_state = GameState.INTERACTIVE
                # l key shows shopping list
                elif event.key == pygame.K_l:
                    self.env.game.players[self.curr_player].render_inventory = False
                    self.env.game.players[self.curr_player].render_shopping_list = True
                    self.env.game.game_state = GameState.INTERACTIVE

                # switch players
                elif event.key == pygame.K_1:
                    self.curr_player = 0
                elif event.key == pygame.K_2:
                    self.curr_player = 1

                elif event.key == pygame.K_c:
                    self.env.step(self.single_player_action(PlayerAction.TOGGLE))

            # player stands still if not moving, player stops holding cart if c button released
            if event.type == pygame.KEYUP:
                self.env.step(self.single_player_action(PlayerAction.NOP))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:  # up
            self.env.step(self.single_player_action(PlayerAction.NORTH))
        elif keys[pygame.K_DOWN]:  # down
            self.env.step(self.single_player_action(PlayerAction.SOUTH))

        elif keys[pygame.K_LEFT]:  # left
            self.env.step(self.single_player_action(PlayerAction.WEST))

        elif keys[pygame.K_RIGHT]:  # right
            self.env.step(self.single_player_action(PlayerAction.EAST))

        self.running = self.env.game.running
        self.env.render()

    def handle_interactive_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.env.game.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.env.game.running = False

                # b key cancels interaction
                elif event.key == pygame.K_b:
                    self.env.step(self.single_player_action(PlayerAction.CANCEL))

                # return key continues interaction
                elif event.key == pygame.K_RETURN:
                    self.env.step(self.single_player_action(PlayerAction.INTERACT))
                # i key turns off inventory rendering
                elif event.key == pygame.K_i:
                    if self.env.game.players[self.curr_player].render_inventory:
                        self.env.game.players[self.curr_player].render_inventory = False
                        self.env.game.game_state = GameState.EXPLORATORY
                # l key turns off shopping list rendering
                elif event.key == pygame.K_l:
                    if self.env.game.players[self.curr_player].render_shopping_list:
                        self.env.game.players[self.curr_player].render_shopping_list = False
                        self.env.game.game_state = GameState.EXPLORATORY
        self.running = self.env.game.running
        self.env.render()


if __name__ == "__main__":

    env = SupermarketEnv(num_players=1, player_speed=0.07, render_messages=True)

    handler = SupermarketEventHandler(env)

    while handler.running:
        handler.handle_events()

