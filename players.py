from cards import Pile, Card


class Player:

    def __init__(self, name, hand=None, points=0):
        """
        :param name: Name of player
        :type name: str
        :param hand: The player's hand
        :type hand: Pile | None
        :param points: The player's points
        :type points: int
        """

        self.name = name
        if hand is None:
            self.hand = Pile()
        else:
            self.hand = hand
        self.points = points

    def display_hand(self):
        """
        Prints the cards in a player's hand together with an identifying number
        """

        self.hand.sort()
        for i, card in enumerate(self.hand.cards):
            print(f"{i + 1}: {card.name}")
        print("\n")

    def draw(self, num, deck):
        """
        Moves cards from the deck to a player's hand, and returns the last drawn card
        :param num: The number of cards to draw
        :type num: int
        :param deck: The deck to draw from
        :type deck: Deck
        :return: The most recent card drawn
        :rtype: Card | None
        """

        drawn_card = None
        for _ in range(num):
            drawn_card = deck.draw()
            self.hand.add(drawn_card)

        return drawn_card

    def draw_and_offer(self, deck, discard_pile):
        """
        When the player has to draw a card, draw it then check if it's playable, if it is offer to play it
        :param deck: The deck to draw cards from
        :type deck: Deck
        :param discard_pile: The discard pile cards are played onto
        :type discard_pile: Pile
        :return: The card played, if any
        :rtype: Card | None
        """

        played_card = None
        drawn_card = self.draw(1, deck)

        if self.playable_card(drawn_card, discard_pile):
            while True:
                play = input(f"You drew {drawn_card.name}, do you want to play it?\t").lower()
                if play in ("y", "yes", "yeah", "yep"):
                    self.play(drawn_card, discard_pile)
                    played_card = drawn_card
                    break
                elif play in ("n", "no", "nah", "nope"):
                    break
                else:
                    print("Please answer (Y)es or (N)o")
        else:
            print(f"You drew {drawn_card.name}, but you can't play it")

        return played_card

    def play(self, card, discard_pile):
        """
        Play the given card from the player's hand, update it's colour if it's a wild-card
        :param card: The card to be played
        :type card: Card
        :param discard_pile: The discard pile cards are played onto
        :type discard_pile: Pile
        """

        # move card from hand to discard pile
        self.hand.remove(card)
        discard_pile.add(card)

        # make card variable specifically the card on top of the discard pile so colour can be changed if necessary
        card = discard_pile.top
        if card.colour == "W":
            card.wild_colour(self)

    def playable_card(self, card, discard_pile):
        """
        Checks if it possible for a given card to be played
        :param card: The card to check
        :type card: Card
        :param discard_pile: The discard pile cards are played onto
        :type discard_pile: Pile
        :return: Whether the card can be played
        :rtype: bool
        """

        top_card = discard_pile.top

        card_playable = False
        attribute_matches = [i == j is not None for i, j in zip(card.attributes, top_card.attributes)]
        colour_matches = [top_card.colour == card.colour for card in self.hand.cards]
        if card == Card("W") or True in attribute_matches:
            card_playable = True
        elif card == Card("W", action="+4") and True not in colour_matches:
            card_playable = True

        return card_playable

    def playable_hand(self, discard_pile):
        """
        Checks if it possible for the player to play any cards from their hand
        :param discard_pile: The discard pile cards are played onto
        :type discard_pile: Pile
        :return: Whether the player can play a card
        :rtype: bool
        """
        hand_playable = False
        for card in self.hand.cards:
            if self.playable_card(card, discard_pile):
                hand_playable = True

        return hand_playable


class Group:

    def __init__(self, *players):
        """
        :param players: A group of players
        :type players: Player
        """

        self.players = list(players)
        self.player_number = None
        self.current_player = None

    @property
    def longest_name(self):
        """
        Finds the length of the longest player name
        :return: The length of the name
        :rtype: int
        """

        return max(len(player.name) for player in self.players)

    @property
    def size(self):
        """
        The number of players in the group
        :return: The number of players
        :rtype: int
        """

        return len(self.players)

    @property
    def standings(self):
        """
        Gives the current standings sorted by number of points
        :return: The standings
        :rtype: list[Player]
        """

        points = [(player.points, player.name, player) for player in self.players]
        points.sort(reverse=True)
        points = [position[2] for position in points]

        return points

    def add(self, player):
        """
        Add a player to the group
        :param player: The player to be added
        :type player: Player
        """

        self.players.append(player)

    def give_points(self):
        """
        Give the current player (the winner) points equal to total value of every other player's cards
        """

        game_points = sum(player.hand.value for player in self.players if player is not self.current_player)
        self.current_player.points += game_points
        print(f"Well done {self.current_player.name}! You've won the game and got {game_points} points!")

    def initial(self, state):
        """
        Determine the player who goes first
        :param state: The state of the game
        :type state: State
        """

        self.player_number = min(state.turn_order, 0) % self.size
        self.current_player = self.players[self.player_number]

    def winner_first(self):
        """
        Causes the winner of the game to go first in the next game by rotating play order
        """

        pos = self.players.index(self.current_player)
        for _ in range(pos):
            player = self.players.pop(0)
            self.add(player)

    def next(self, state):
        """
        Moves on to the next player based on the turn order
        :param state: The state of the game
        :type state: State
        """

        self.player_number = (self.player_number + state.turn_order) % self.size
        self.current_player = self.players[self.player_number]


class State:

    def __init__(self, turn_order=1, skip=0, forced_draw=0):
        """
        :param turn_order: 1 if turn order is normal, -1 if it's reversed
        :type turn_order: int
        :param skip: The number of turns to skip, 0 normally
        :type skip: int
        :param forced_draw: The number of cards the next player is forced to draw, 0 normally
        :type forced_draw: int
        """

        self.turn_order = turn_order
        self.skip = skip
        self.forced_draw = forced_draw

    def neutralise(self):
        """
        Removes any turn skipping, forced draws or colour choice, but leaves turn order as is
        """

        self.skip = 0
        self.forced_draw = 0

    def update(self, card):
        """
        Updates state of the game based on the action of the played card
        :param card: The played card
        :type card: Card
        """

        if card.action == "rev":
            self.turn_order *= -1
            self.neutralise()
        elif card.action == "skip":
            self.skip = 1
            self.forced_draw = 0
        elif "+" in str(card.action):
            self.skip = 1
            self.forced_draw = int(card.action[1:])
        else:
            self.neutralise()
