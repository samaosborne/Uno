from functools import total_ordering
from random import shuffle


@total_ordering
class Card:
    """
    A one sided card with colour, number and/or an action
    """

    def __init__(self, colour, number=None, action=None):
        """
        :param colour: Colour of card (R for red, G for green, B for blue, Y for yellow, W for wild)
        :type colour: str
        :param number: Number on card (None if action card)
        :type number: int | None
        :param action: Action of card (None if number card)
        :type action: str | None
        """

        self.colour = colour
        self.number = number
        self.action = action

    def __eq__(self, other):
        """
        Overrides default implementation of equality
        :param other: The object to compare to
        :type other: object
        :return: Whether compared objects are equivalent
        :rtype: bool
        """

        if not isinstance(other, Card):
            return NotImplemented

        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        """
        Overrides default implementation of less than
        :param other: The object to compare to
        :type other: object
        :return: Whether compared objects are equivalent
        :rtype: bool
        """

        if not isinstance(other, Card):
            return NotImplemented

        self_dic = {key: value for (key, value) in self.__dict__.items()}
        other_dic = {key: value for (key, value) in other.__dict__.items()}

        # replace missing attributes (and wild colour) with values more extreme than exist on cards
        for dic in (self_dic, other_dic):
            if dic["_colour"] == "W":
                dic["_colour"] = "Z"
            if dic["number"] is None:
                dic["number"] = 10
            if dic["action"] is None:
                dic["action"] = "+"

        # check the attributes for order, continuing to next only on equality
        for key in self_dic:
            if self_dic[key] < other_dic[key]:
                return True
            elif self_dic[key] > other_dic[key]:
                return False

        # if all attributes are equal return false
        return False

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        if colour in ("R", "G", "B", "Y", "W"):
            self._colour = colour
        else:
            raise ValueError("Not a possible colour")

    @property
    def attributes(self):
        """
        Gives a list of the attributes of the card
        :return: The list of attributes
        :rtype: list[str, int, str]
        """

        return [attribute for attribute in self.__dict__.values()]

    @property
    def name(self):
        """
        Gives the name of the card
        :return: Name of card
        :rtype: str
        """

        return " ".join(str(attribute) for attribute in self.attributes if attribute is not None)

    @property
    def value(self):
        """
        Returns the point value of the card
        :return: The point value of the card
        :rtype: int
        """

        if self.number is not None:
            return self.number
        else:
            if self.action in ("+2", "rev", "skip"):
                return 20
            else:
                return 50

    def wild_colour(self, player):
        """
        If a wild-card was played change it's colour to match the player's choice
        :param player: The wild-card played
        :type player: players.Player
        """

        colour = "W"
        while colour not in ("R", "G", "B", "Y"):
            colour = input(f"{player.name}, what colour would you like the wild-card to be?\n"
                           f"(R)ed, (G)reen, (B)lue or (Y)ellow?\t").upper()
            try:
                self.colour = colour
                break
            except ValueError:
                print("That's not a valid colour, try again")


class Pile:
    """
    An ordered pile of cards that doesn't need to be shuffled or drawn from,
    used for the discard pile and players' hands
    """

    def __init__(self, *cards):
        """
        :param card: A collection of cards
        :type card: Card
        """

        self.cards = list(cards)

    @property
    def size(self):
        """
        Returns the number of cards in the pile
        :return: The number of cards
        :rtype: int
        """

        return len(self.cards)

    @property
    def top(self):
        """
        Returns the top card of the pile
        :return: The top card
        :rtype: Card
        """

        return self.cards[-1]

    @property
    def value(self):
        """
        Gives the total value of all cards in the pile
        :return: The total value
        :rtype: int
        """

        return sum(card.value for card in self.cards)

    def add(self, card, quantity=1):
        """
        Adds cards to the deck
        :param card: The card to add
        :type card: Card
        :param quantity: The number of that card to add
        :type quantity: int
        """

        for _ in range(quantity):
            if card.colour == "W":
                # set up an empty card in order to make a copy of it and add the copy for each so changing colour of one
                # wild-card doesn't affect the others
                card_copy = Card("W")
                attributes = {key: value for (key, value) in card.__dict__.items()}
                card_copy.__dict__ = attributes
                self.cards.append(card_copy)
            else:
                self.cards.append(card)

    def remove(self, card):
        """
        Removes a card from the deck
        :param card: The card to remove
        :type card: Card
        """

        self.cards.remove(card)

    def reset(self, deck):
        """
        Shuffles all but the top card of the discard pile to reset the deck
        :param deck: The game's deck
        :type deck: Deck
        """

        for card in self.cards[:-1]:
            if card.number is None and card.action in (None, "+4"):
                card.colour = "W"
        deck.cards = self.cards[-1]
        self.cards = [self.top]
        deck.shuffle()
        print("The deck was empty so the discard pile has been shuffled back in to the deck!")

    def sort(self):
        """
        Sorts the pile by colour, then number, then action
        """

        self.cards.sort()


class Deck(Pile):
    """
    An ordered pile of cards that can be shuffled and drawn from,
    used for the deck
    """

    def __init__(self, *cards):
        """
        :param cards: The cards in the starting deck
        :type cards: Card
        """

        super().__init__(*cards)

    def deal(self, group):
        """
        Deal an opening hand to each player in the game
        :param group: The group of players
        :type group: players.Group
        """

        for player in group.players:
            player.hand = Pile()
            player.draw(7, self)

    def draw(self):
        """
        Removes and returns the top card of the deck
        :return: The drawn card
        :rtype: Card
        """

        return self.cards.pop(-1)

    def shuffle(self):
        """
        Shuffles the deck
        """

        shuffle(self.cards)
