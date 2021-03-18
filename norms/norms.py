from collections import defaultdict

from enums.player_action import PlayerAction
from helper import pos_collision
from norms.norm import Norm, NormViolation
from shelves import Shelf


class CartTheftViolation(NormViolation):
    def __init__(self, player, cart):
        super().__init__()
        self.thief = player
        self.cart = cart

    def __eq__(self, other):
        return isinstance(other, CartTheftViolation) and (self.thief, self.cart) == (other.thief, other.cart)

    def __hash__(self):
        return hash((self.thief, self.cart))

    def as_string(self):
        return "{player} stole a cart from {owner}".format(player=self.thief, owner=self.cart.owner)


class CartTheftNorm(Norm):
    def __init__(self):
        super(CartTheftNorm, self).__init__()

    def post_monitor(self, game, action):
        new_violations = set()
        for player in game.players:
            cart = player.curr_cart
            if cart is not None and cart.owner != player:
                violation = CartTheftViolation(player, cart)
                if violation not in self.known_violations:
                    self.known_violations.add(violation)
                    new_violations.add(violation)
        return new_violations

    def reset(self):
        super(CartTheftNorm, self).reset()


class ShopliftingViolation(NormViolation):
    def __init__(self, thief, stolen_food):
        super(ShopliftingViolation, self).__init__()
        self.thief = thief
        self.stolen_food = stolen_food

    def __eq__(self, other):
        return isinstance(other, ShopliftingViolation) and self.thief == other.thief

    def __hash__(self):
        return hash(self.thief)

    def as_string(self):
        return "{player} shoplifted".format(player=self.thief)


class ShopliftingNorm(Norm):
    def __init__(self):
        super(ShopliftingNorm, self).__init__()

    def post_monitor(self, game, action):
        new_violations = set()
        for player in game.players:
            if player.position[0] >= 0:
                continue
            stolen_food = []
            if player.curr_cart is not None:
                cart = player.curr_cart
                stolen_food.extend(cart.contents)
            elif player.holding_food is not None and not player.bought_holding_food:
                stolen_food.append((player.holding_food, 1))
            if len(stolen_food) > 0:
                violation = ShopliftingViolation(player, stolen_food)
                if violation not in self.known_violations:
                    self.known_violations.add(violation)
                    new_violations.add(violation)
        return new_violations

    def reset(self):
        super(ShopliftingNorm, self).reset()


class WrongShelfViolation(NormViolation):
    def __init__(self, player, holding_food, shelf):
        super(WrongShelfViolation, self).__init__()
        self.player = player
        self.shelf = shelf
        self.holding_food = holding_food

    # No eq or hash implementation; if this isn't the same object, it's not equal

    def as_string(self):
        return "{player} put the {holding_food} on the {shelf_food} shelf.".format(player=self.player,
                                                                                   holding_food=self.holding_food,
                                                                                   shelf_food=self.shelf.string_type)


class WrongShelfNorm(Norm):
    def pre_monitor(self, game, action):
        violations = set()
        for i, player in enumerate(game.players):
            if player.holding_food is not None and action[i] == PlayerAction.INTERACT:
                interaction_object = game.interaction_object(player)
                if isinstance(interaction_object, Shelf) and interaction_object.string_type != player.holding_food:
                    violations.add(WrongShelfViolation(player, player.holding_food, interaction_object))
        return violations


class PlayerCollisionViolation(NormViolation):
    def __init__(self, collider, collidee):
        super().__init__()
        self.collider = collider
        self.collidee = collidee

    def as_string(self):
        return "{collider} collided with {collidee}".format(collider=self.collider, collidee=self.collidee)


class PlayerCollisionNorm(Norm):
    def pre_monitor(self, game, action):
        violations = set()
        next_positions = [game.next_position(player, action[i]) for i, player in enumerate(game.players)]
        for i, player in enumerate(game.players):
            for j, player2 in enumerate(game.players):
                if i == j:
                    continue
                if 1 <= action[i] <= 4 and pos_collision(next_positions[i][0], next_positions[i][1],
                                                         next_positions[j][0],
                                                         next_positions[j][1], x_margin=0.55, y_margin=0.55):
                    if (player, player2) not in self.old_collisions:
                        violations.add(PlayerCollisionViolation(collider=player, collidee=player2))
                        self.old_collisions.add((player, player2))
                elif (player, player2) in self.old_collisions:
                    self.old_collisions.remove((player, player2))
        return violations

    def reset(self):
        super(PlayerCollisionNorm, self).reset()
        self.old_collisions = set()

    def __init__(self):
        super(PlayerCollisionNorm, self).__init__()
        self.old_collisions = set()


class ObjectCollisionViolation(NormViolation):
    def __init__(self, collider, obj):
        super().__init__()
        self.collider = collider
        self.obj = obj

    def as_string(self):
        return "{collider} ran into {obj}".format(collider=self.collider, obj=self.obj)


class ObjectCollisionNorm(Norm):
    def pre_monitor(self, game, action):
        violations = set()
        for i, player in enumerate(game.players):
            next_pos = game.next_position(player, action[i])
            for obj in game.objects:
                if player.curr_cart is not None and obj == player.curr_cart:
                    continue
                if 1 <= action[i] <= 4 and obj.collision(next_pos[0], next_pos[1]):
                    if (player, obj) not in self.old_collisions:
                        violations.add(ObjectCollisionViolation(player, obj))
                        self.old_collisions.add((player, obj))
                elif (player, obj) in self.old_collisions:
                    self.old_collisions.remove((player, obj))
        return violations

    def reset(self):
        super(ObjectCollisionNorm, self).reset()
        self.old_collisions = set()

    def __init__(self):
        super(ObjectCollisionNorm, self).__init__()
        self.old_collisions = set()


class WallCollisionViolation(NormViolation):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def as_string(self):
        return "{player} ran into a wall".format(player=self.player)


class WallCollisionNorm(Norm):
    def pre_monitor(self, game, action):
        new_violations = set()
        for i, player in enumerate(game.players):
            next_pos = game.next_position(player, action[i])
            if 1 <= action[i] <= 4 and game.map[round(next_pos[1])][round(next_pos[0])] != "F" and \
                    game.map[round(next_pos[1])][round(next_pos[0])] != "Y":
                if player not in self.old_collisions:
                    new_violations.add(WallCollisionViolation(player))
                    self.old_collisions.add(player)
            elif player in self.old_collisions:
                self.old_collisions.remove(player)
        return new_violations

    def reset(self):
        super(WallCollisionNorm, self).reset()
        self.old_collisions = set()

    def __init__(self):
        super(WallCollisionNorm, self).__init__()
        self.old_collisions = set()


# TODO need a version of collision norm for when the player is holding a shopping cart
def in_exit_zone(player):
    return player.position[0] <= 1.1 and (6.5 <= player.position[1] <= 7.5 or 2.5 <= player.position[1] <= 3.5)


def in_entrance_zone(player):
    return player.position[0] <= 1.1 and 14.5 <= player.position[1] <= 15.5


class BlockingExitViolation(NormViolation):
    def __init__(self, player, entrance):
        super().__init__()
        self.entrance = entrance
        self.player = player

    def as_string(self):
        exit_or_entrance_str = "entrance" if self.entrance else "exit"
        return "{player} is blocking an {e}".format(player=self.player, e=exit_or_entrance_str)


class BlockingExitNorm(Norm):
    def __init__(self, time_threshold=30):
        self.time_threshold = time_threshold
        self.time_in_exit = defaultdict(int)
        self.old_violations = set()

    def post_monitor(self, game, action):
        violations = set()
        for player in game.players:
            if in_exit_zone(player) or in_entrance_zone(player):
                self.time_in_exit[player] += 1
                if self.time_in_exit[player] >= self.time_threshold and player not in self.old_violations:
                    print(self.time_in_exit[player])
                    self.old_violations.add(player)
                    if in_entrance_zone(player):
                        violations.add(BlockingExitViolation(player, True))
                    elif in_exit_zone(player):
                        violations.add(BlockingExitViolation(player, False))
            else:
                if player in self.old_violations:
                    self.old_violations.remove(player)
                self.time_in_exit[player] = 0
        return violations

    def reset(self):
        super(BlockingExitNorm, self).reset()
        self.old_violations = set()
        self.time_in_exit = defaultdict(int)


class EntranceOnlyViolation(NormViolation):
    def __init__(self, player):
        super(EntranceOnlyViolation, self).__init__()
        self.player = player

    def as_string(self):
        return "{player} exited through an entrance".format(player=self.player)


class EntranceOnlyNorm(Norm):
    def post_monitor(self, game, action):
        violations = set()
        for player in game.players:
            if player.position[0] < 0 and in_entrance_zone(player):
                violations.add(EntranceOnlyViolation(player))
        return violations


class ObstructionNorm(Norm):
    def post_monitor(self, game, action):
        return set()

    def reset(self):
        super(ObstructionNorm, self).reset()

    def __init__(self):
        super(ObstructionNorm, self).__init__()


class UnattendedCartNorm(Norm):
    def post_monitor(self, game, action):
        pass
