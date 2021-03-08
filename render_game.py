import pygame
import config
from map_library import map_tile_image

# right now the rendering functions aren't part of a class, not sure if that goes against python etiquette :/


def render_objects_and_players(screen, camera, objects, players, carts):
    to_render = sorted(players + objects, key=lambda x: x.position[1])
    for obj in to_render:
        if obj in players:
            obj.render(screen, camera, carts)
        else:
            obj.render(screen, camera)


def render_decor(screen, camera):
    window = pygame.transform.scale(pygame.image.load("images/decor/window.png"),
                                    (int(2.6 * config.SCALE), int(1.5 * config.SCALE)))
    screen.blit(window, (int(15.6 * config.SCALE) - (camera.position[0] * config.SCALE),
                         int(.25 * config.SCALE) - (camera.position[1] * config.SCALE)))
    arrow_sign = pygame.transform.scale(pygame.image.load("images/decor/arrow.png"),
                                        (int(0.5 * config.SCALE), int(.4 * config.SCALE)))
    screen.blit(arrow_sign, (int(1.5 * config.SCALE) - (camera.position[0] * config.SCALE),
                             int(.8 * config.SCALE) - (camera.position[1] * config.SCALE)))
    doormat = pygame.transform.scale(pygame.image.load("images/decor/doormat.png"),
                                     (int(config.SCALE), int(config.SCALE)))
    screen.blit(doormat, (int(0 * config.SCALE) - (camera.position[0] * config.SCALE),
                          int(12 * config.SCALE) - (camera.position[1] * config.SCALE)))
    exit_mat = pygame.transform.scale(pygame.image.load("images/decor/exit_mat.png"),
                                      (int(config.SCALE), int(config.SCALE)))
    screen.blit(exit_mat, (int(0 * config.SCALE) - (camera.position[0] * config.SCALE),
                           int(7 * config.SCALE) - (camera.position[1] * config.SCALE)))
    screen.blit(exit_mat, (int(0 * config.SCALE) - (camera.position[0] * config.SCALE),
                           int(3 * config.SCALE) - (camera.position[1] * config.SCALE)))


# Rendering map
def render_map(screen, camera, player, tile_map):
    camera.determine_camera(player, tile_map)

    y_pos = 0
    for line in tile_map:
        x_pos = 0
        for tile in line:
            image = map_tile_image[tile]
            rect = pygame.Rect(x_pos * config.SCALE - (camera.position[0] * config.SCALE),
                               y_pos * config.SCALE - (camera.position[1] * config.SCALE),
                               config.SCALE, config.SCALE)
            screen.blit(image, rect)
            x_pos = x_pos + 1
        y_pos = y_pos + 1


def render_interactions(game, screen, objects):
    for player in game.players:
        if player.render_inventory:
            player.render_items(screen, game.carts)
        if player.render_shopping_list:
            player.render_list(screen, game.carts)

    for object in objects:
        object.render_interaction(game, screen)


# not being used right now
def render_pickup(screen):
    textbox = pygame.transform.scale(pygame.image.load("text/textbox.png"),
                                     (int(640), int(150)))
    screen.blit(textbox, (int(0 * config.SCALE), int(330)))
    text = render_text("Your number has been called.", False)
    screen.blit(text, (17, 380))


def render_text(string, bold):
    font = pygame.font.Font("text/pokemonfont.ttf", 17)
    if bold:
        font.bold = True
    text = font.render(string, True, (0, 0, 0))
    return text


def render_textbox(screen, text):
    textbox = pygame.transform.scale(pygame.image.load("text/textbox.png"),
                                     (int(640), int(150)))
    screen.blit(textbox, (int(0 * config.SCALE), int(330)))
    split_text = text.split(" ")
    x_coord = 0
    y_coord = 380
    for word in split_text:
        candidate_x = x_coord+17*(1 + len(word))
        if candidate_x > 623:
            y_coord += 30
            x_coord = 0
        text = render_text(" " + word, False)
        screen.blit(text, (x_coord, y_coord))
        x_coord += 17*(1+len(word))