from enums.player_action import PlayerAction
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
        return "Player {player} stole a cart from {owner}".format(player=self.thief, owner=self.cart.owner)


class CartTheftNorm(Norm):
    def __init__(self):
        super(CartTheftNorm, self).__init__()

    def monitor(self, game, action):
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
        return "Player {player} shoplifted".format(player=self.thief)


class ShopliftingNorm(Norm):
    def __init__(self):
        super(ShopliftingNorm, self).__init__()

    def monitor(self, game, action):
        new_violations = set()
        for player in game.players:
            if player.position[0] > 1:
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
    def preprocess(self, game, action):
        for i, player in enumerate(game.players):
            if player.holding_food is not None and action[i] == PlayerAction.INTERACT:
                interaction_object = game.interaction_object(player)
                if isinstance(interaction_object, Shelf) and interaction_object.string_type != player.holding_food:
                    self.violations.add(WrongShelfViolation(player, player.holding_food, interaction_object))

    def monitor(self, game, action):
        new_violations = self.violations
        self.violations = set()
        return new_violations

    def reset(self):
        super().reset()

    def __init__(self):
        super(WrongShelfNorm, self).__init__()
        self.violations = set()


class PlayerCollisionNorm(Norm):
    def monitor(self, game, action):
        return set()

    def reset(self):
        super(PlayerCollisionNorm, self).reset()
        
    def __init__(self):
        super(PlayerCollisionNorm, self).__init__()
        
        
class ObjectCollisionNorm(Norm):
    def monitor(self, game, action):
        return set()
    
    def reset(self):
        super(ObjectCollisionNorm, self).reset()
        
    def __init__(self):
        super(ObjectCollisionNorm, self).__init__()


class ObstructionNorm(Norm):
    def monitor(self, game, action):
        return set()

    def reset(self):
        super(ObstructionNorm, self).reset()

    def __init__(self):
        super(ObstructionNorm, self).__init__()


class UnattendedCartNorm(Norm):
    def monitor(self, game, action):
        pass