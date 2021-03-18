import time

import gym
import pygame

import config
from enums.player_action import PlayerAction
from game import Game

MOVEMENT_ACTIONS = [PlayerAction.NORTH, PlayerAction.SOUTH, PlayerAction.EAST, PlayerAction.WEST]


class SupermarketEnv(gym.Env):

    def __init__(self, num_players=1, player_speed=0.15, render_messages=False):
        pygame.init()
        super(SupermarketEnv, self).__init__()

        pygame.display.set_caption("Supermarket Environment")

        self.clock = pygame.time.Clock()
        self.step_count = 0
        self.render_messages = render_messages

        self.num_players = num_players
        self.player_speed = player_speed
        self.game = None

        self.action_space = gym.spaces.MultiDiscrete([len(PlayerAction)]*self.num_players)
        self.observation_space = gym.spaces.Dict()

    def step(self, action):
        done = False
        for i, player_action in enumerate(action):
            if player_action in MOVEMENT_ACTIONS:
                self.game.player_move(i, player_action)
            elif player_action == PlayerAction.NOP:
                self.game.nop(i)
            elif player_action == PlayerAction.INTERACT:
                self.game.interact(i)
            elif player_action == PlayerAction.TOGGLE:
                self.game.toggle_cart(i)
            elif player_action == PlayerAction.CANCEL:
                self.game.cancel_interaction(i)
        observation = self.game.update_observation()
        self.step_count += 1
        if not self.game.running:
            done = True
        return observation, 0., done, None

    def reset(self):
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.game = Game(screen, self.num_players, self.player_speed, render_messages=self.render_messages)
        self.game.set_up()
        self.step_count = 0
        return self.game.update_observation()

    def render(self, mode='human'):
        self.clock.tick(120)
        if self.game.running:
            self.game.update()
            pygame.display.flip()
        else:
            pygame.quit()


if __name__ == "__main__":
    env = SupermarketEnv(2)
    env.reset()

    for i in range(100):
        env.step((PlayerAction.EAST, PlayerAction.SOUTH))
        env.render()