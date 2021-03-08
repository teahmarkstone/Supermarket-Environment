from norms.norm import Norm


class CartTheftNorm(Norm):

    def __init__(self):
        super(CartTheftNorm, self).__init__()

    def monitor(self, game):
        new_instances = set()
        for player in game.players:
            cart = player.curr_cart
            if cart is not None and cart.owner != player:
                # Found a stolen cart!
                if (player, cart) not in self.known_instances:
                    self.known_instances.add((player, cart))
                    self.write_instance(game, (player, cart))
        for instance in new_instances:
            self.write_instance(game, instance)

    def write_instance(self, game, instance):
        player, cart = instance
        print("Player ", player, " stole a cart from ", cart.owner)
