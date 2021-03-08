from enums.direction import Direction


def obj_collision(obj,  x_position, y_position, x_margin=0.55, y_margin=0.55):
    return obj.position[0] - x_margin < x_position < obj.position[0] + obj.width + x_margin and \
           obj.position[1] - y_margin < y_position < obj.position[1] + obj.height + y_margin

def can_interact_default(obj, player, range=0.5):
    if player.direction == Direction.NORTH:
        return obj.collision(player.position[0], player.position[1] - range)
    elif player.direction == Direction.SOUTH:
        return obj.collision(player.position[0], player.position[1] + range)
    elif player.direction == Direction.WEST:
        return obj.collision(player.position[0] - range, player.position[1])
    elif player.direction == Direction.EAST:
        return obj.collision(player.position[0] + range, player.position[1])
    return False