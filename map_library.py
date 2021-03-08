import pygame
import config

# library for text map
map_tile_image = {
    # top and bottom
    "V": pygame.transform.scale(pygame.image.load("images/floor_wall/ul_corner.png"), (config.SCALE, config.SCALE)),
    "U": pygame.transform.scale(pygame.image.load("images/floor_wall/ur_corner.png"), (config.SCALE, config.SCALE)),
    "v": pygame.transform.scale(pygame.image.load("images/floor_wall/bl_corner.png"), (config.SCALE, config.SCALE)),
    "u": pygame.transform.scale(pygame.image.load("images/floor_wall/br_corner.png"), (config.SCALE, config.SCALE)),
    "M": pygame.transform.scale(pygame.image.load("images/floor_wall/u_wall.png"), (config.SCALE, config.SCALE)),
    "m": pygame.transform.scale(pygame.image.load("images/floor_wall/b_floor.png"), (config.SCALE, config.SCALE)),

    "B": pygame.transform.scale(pygame.image.load("images/floor_wall/b_wall2.png"), (config.SCALE, config.SCALE)),
    "W": pygame.transform.scale(pygame.image.load("images/floor_wall/b_wall.png"), (config.SCALE, config.SCALE)),
    "Y": pygame.transform.scale(pygame.image.load("images/floor_wall/floor_wall.png"), (config.SCALE, config.SCALE)),
    "X": pygame.transform.scale(pygame.image.load("images/floor_wall/b_wall3.png"), (config.SCALE, config.SCALE)),

    "F": pygame.transform.scale(pygame.image.load("images/floor_wall/floor.png"), (config.SCALE, config.SCALE)),
    "L": pygame.transform.scale(pygame.image.load("images/floor_wall/L_wall_floor.png"), (config.SCALE, config.SCALE)),
    "R": pygame.transform.scale(pygame.image.load("images/floor_wall/R_wall_floor.png"), (config.SCALE, config.SCALE)),

    "0": pygame.transform.scale(pygame.image.load("images/floor_wall/floor.png"), (config.SCALE, config.SCALE)),
    "1": pygame.transform.scale(pygame.image.load("images/floor_wall/extra_1.png"), (config.SCALE, config.SCALE)),
    "2": pygame.transform.scale(pygame.image.load("images/floor_wall/extra_2.png"), (config.SCALE, config.SCALE))
}
