from norms.norm import Norm, NormViolation


class CartTheft(NormViolation):
    def __init__(self, player, cart):
        super().__init__()
        self.thief = player
        self.cart = cart

    def __eq__(self, other):
        return isinstance(other, CartTheft) and (self.thief, self.cart) == (other.thief, other.cart)

    def __hash__(self):
        return hash((self.thief, self.cart))

    def as_string(self):
        return "Player {player} stole a cart from {owner}".format(player=self.thief, owner=self.cart.owner)


class CartTheftNorm(Norm):
    def __init__(self):
        super(CartTheftNorm, self).__init__()

    def monitor(self, game):
        new_violations = set()
        for player in game.players:
            cart = player.curr_cart
            if cart is not None and cart.owner != player:
                violation = CartTheft(player, cart)
                if violation not in self.known_violations:
                    self.known_violations.add(violation)
                    new_violations.add(violation)
        return new_violations

    def reset(self):
        super(CartTheftNorm, self).reset()