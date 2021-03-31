import pygame
import random
from PIL import Image


def build_sprites():
    # loads all sprite sheets, returns two random ones
    sprite_sheet = load_sheets()
    sprites = splice_and_merge([48, 72], sprite_sheet)
    return sprites


def pick_sprites(sprite_sheets):
    rand_sheet = sprite_sheets[random.randint(0, 9)]
    return rand_sheet


def load_sheets():
    sprite_sheets = [pygame.image.load("images/sprites/sprite_sheets/Adam.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Alex.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Amelia.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Lucy.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Molly.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Old_man_Josh.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Old_woman_Jenny.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Pier.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Roki.png").convert_alpha(),
                     pygame.image.load("images/sprites/sprite_sheets/Samuel.png").convert_alpha()]
    rand_sheet = pick_sprites(sprite_sheets)
    return rand_sheet


def splice_and_merge(size, sheet, pos=(0, 24)):
    len_sprt_x, len_sprt_y = size  # sprite size
    sprt_rect_x, sprt_rect_y = pos  # where to find first sprite on sheet
    sheet_rect = sheet.get_rect()
    sprites = []
    for i in range(0, sheet_rect.height - len_sprt_y, size[1]):  # rows

        for i in range(0, sheet_rect.width - len_sprt_x, size[0]):  # columns

            sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y))  # find sprite you want
            sprite = sheet.subsurface(sheet.get_clip())  # grab the sprite you want
            # new_sprite = Image.new('RGB', (69, 69), ())
            # new_sprite.paste()
            # pil_string_image = pygame.image.tostring(sprite, "RGBA", False)
            # print(size)
            # pil_image = Image.frombytes("RGBA", size, pil_string_image)
            # sprite = add_margin(pil_image, 10, 10, 10, 10, (0))
            # new_size = sprite.size
            # mode = sprite.mode
            # # print(size)
            # sprite = sprite.tobytes()
            # sprite = pygame.image.fromstring(sprite, new_size, mode)
            sprites.append(sprite)
            sprt_rect_x += len_sprt_x

        sprt_rect_y += len_sprt_y
        sprt_rect_x = 0
    print(len(sprites))
    return sprites

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

# steps for sprite building
# randomly choose two sprite sheets (head and torso)
# start building (24 images-- 6 images per direction)
#   using above code to splice head and body, then other code to merge the two and save as one image,
#   append to correct north/south/east/west array
