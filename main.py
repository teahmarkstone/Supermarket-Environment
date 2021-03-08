import pygame
import config
from game import Game
from norms.theft import CartTheftNorm

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    pygame.display.set_caption("Supermarket Environment")

    clock = pygame.time.Clock()

    num_players = 1
    game = Game(screen, num_players)

    game.set_up()

    # I added the option for music about a month ago, not necessary but fun :) should work if uncommented
    # pygame.mixer.music.load("elevator_music.wav")
    # pygame.mixer.music.play(-1)
    norms = [CartTheftNorm()]

    while game.running:

        clock.tick(120)
        game.update()
        for norm in norms:
            norm.monitor(game)

        pygame.display.flip()

    pygame.quit()
    quit()

